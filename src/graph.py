# -*- coding: utf-8 -*-
"""多智能体编排：LangGraph 状态图；依赖不可用时自动回退为顺序编排器。"""
from typing import TypedDict, List


class AgentState(TypedDict, total=False):
    user_query: str
    lang: str
    route: str
    device: str
    alarm_code: str
    retrieved: list
    causes: List[str]
    checks: List[str]
    refs: List[str]
    stock: list
    work_order: str
    audit_note: str
    final: str
    suggestions: List[str]
    trace: list
    qa: dict
    qa_case: dict


class SimpleGraph:
    """与状态图同构的顺序编排器（回退方案，无外部依赖）。"""

    def __init__(self):
        from .agents import (TriageAgent, QAAgent, RetrievalAgent, DiagnosisAgent,
                             SpareOrderAgent, AuditAgent, ReplyAgent)
        self.triage = TriageAgent()
        self.qa = QAAgent()
        self.retrieval = RetrievalAgent()
        self.diagnosis = DiagnosisAgent()
        self.spare = SpareOrderAgent()
        self.audit = AuditAgent()
        self.reply = ReplyAgent()

    def invoke(self, state):
        state = self.triage.run(state)
        route = state.get('route')
        if route == 'normal':
            state = self.retrieval.run(state)
            state = self.diagnosis.run(state)
            state = self.spare.run(state)
        elif route == 'qa':
            state = self.qa.run(state)
        state = self.audit.run(state)
        state = self.reply.run(state)
        return state


class LangGraphWrapper:
    def __init__(self, graph):
        self._graph = graph

    def invoke(self, state):
        return self._graph.invoke(state)


def build_graph():
    try:
        from langgraph.graph import StateGraph, END
        from .agents import (TriageAgent, QAAgent, RetrievalAgent, DiagnosisAgent,
                             SpareOrderAgent, AuditAgent, ReplyAgent)
        triage = TriageAgent()
        qa = QAAgent()
        retrieval = RetrievalAgent()
        diagnosis = DiagnosisAgent()
        spare = SpareOrderAgent()
        audit = AuditAgent()
        reply = ReplyAgent()

        g = StateGraph(AgentState)
        g.add_node('triage', triage.run)
        g.add_node('qa', qa.run)
        g.add_node('retrieval', retrieval.run)
        g.add_node('diagnosis', diagnosis.run)
        g.add_node('spare_order', spare.run)
        g.add_node('audit', audit.run)
        g.add_node('reply', reply.run)
        g.set_entry_point('triage')

        def route_after_triage(state):
            r = state.get('route')
            return r if r in ('normal', 'high_risk', 'reject', 'qa') else 'normal'

        g.add_conditional_edges('triage', route_after_triage, {
            'normal': 'retrieval',
            'qa': 'qa',
            'high_risk': 'audit',
            'reject': 'audit',
        })
        g.add_edge('retrieval', 'diagnosis')
        g.add_edge('diagnosis', 'spare_order')
        g.add_edge('spare_order', 'audit')
        g.add_edge('qa', 'audit')
        g.add_edge('audit', 'reply')
        g.add_edge('reply', END)
        return LangGraphWrapper(g.compile())
    except Exception:
        return SimpleGraph()
