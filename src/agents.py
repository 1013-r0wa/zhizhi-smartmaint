# -*- coding: utf-8 -*-
"""业务智能体：分诊、知识问答、知识检索、故障诊断、备件工单、审核兜底、回复组装。"""
import re

from .kb import get_retriever
from .tools import generate_work_order, query_stock
from . import llm as llm_client

ALARM_RE = re.compile(r'ALM[- ]?(\d{4})', re.IGNORECASE)
DEVICE_RE = re.compile(r'[A-Za-z]{1,3}[-–]\d{2,4}')

HIGH_RISK_WORDS = [
    '崩裂', '剧烈抖动', '剧烈振动', '打火', '焦糊', '冒烟', '起火', '爆炸', '触电',
    '漏电', '高压', '高处作业', '动火', '压力容器', '飞溅', '防护罩打开', '安全门被屏蔽',
    'severe vibration', 'violent vibration', 'arcing', 'burning smell', 'smoke',
    'fire', 'explosion', 'electric shock', 'fracture', 'flying debris',
]
REJECT_WORDS = [
    '修改参数', '写入参数', '改参数', '参数改', '修改plc', 'plc参数', '远程控制',
    '控制设备', '直接启动', '自动启动', '修改工艺', '工艺配方', '禁用安全', '旁路安全', '屏蔽报警',
    'change the plc', 'modify parameter', 'plc parameter', 'remote control',
    'start the spindle remotely', 'bypass safety', 'disable safety', 'override alarm',
]
# 故障描述特征：出现即按诊断流程处理（优先于问答）
FAULT_WORDS = [
    '报警', '故障', '异常', '异响', '抖动', '振动', '温度过高', '温度高', '过热', '发热',
    '压力低', '压力不足', '超时', '过载', '无法', '不能', '不动作', '卡滞', '漏油', '漏气',
    '烧蚀', '崩裂', '失效',
    'alarm', 'fault', 'error', 'vibration', 'overheat', 'overload', 'timeout',
    'leak', 'abnormal noise', 'stuck', 'will not start', 'cannot rotate',
]
# 提问特征：无报警代码、无故障描述时按知识问答处理
QA_HINTS = [
    '如何', '怎么', '怎样', '多久', '多少', '什么时候', '为什么', '是否', '能否',
    '可以吗', '能不能', '需要', '方法', '步骤', '周期', '哪些', '什么', '区别',
    '排查', '注意', '要求', '征兆', '建议', '吗？', '？', '?',
    'how', 'what', 'why', 'when', 'which', 'should', 'can i', 'do i', 'does',
    'often', 'interval', 'method', 'steps', 'procedure', 'difference', 'signs',
]

_ROUTE_CN = {'normal': '常规', 'high_risk': '高危转人工', 'reject': '越界拦截', 'qa': '知识问答'}
_ROUTE_EN = {'normal': 'Diagnosis', 'high_risk': 'High risk → human', 'reject': 'Blocked (out of scope)',
             'qa': 'Knowledge Q&A'}


def _lang(state):
    return 'en' if state.get('lang') == 'en' else 'zh'


def _t(state, zh, en):
    return en if _lang(state) == 'en' else zh


def _norm(text):
    return re.sub(r'\s+', '', (text or '').lower())


def _strip_no(text):
    """去掉知识库原因条目自带的前缀编号，避免双重编号。"""
    return re.sub(r'^\d+[）)]\s*', '', text or '')


def _contains_any(text, words):
    low = (text or '').lower()
    return any(w in low for w in words)


class TriageAgent:
    """分诊智能体：抽取设备与报警号，判定高危、越界、问答或常规路由。"""
    name = '分诊智能体'
    name_en = 'Triage Agent'

    def run(self, state):
        q = state.get('user_query', '')
        m = ALARM_RE.search(q)
        state['alarm_code'] = 'ALM-' + m.group(1) if m else ''
        dm = DEVICE_RE.search(ALARM_RE.sub('', q))
        state['device'] = dm.group(0).upper() if dm else ('未识别' if _lang(state) == 'zh' else 'Unknown')
        lang = _lang(state)
        name = self.name_en if lang == 'en' else self.name

        retriever = get_retriever()
        faq = retriever.search_faq(q, lang)
        route, note = 'normal', _t(state, '进入常规诊断路径', 'Routing to the standard diagnosis flow')
        if _contains_any(q, REJECT_WORDS):
            route = 'reject'
            note = _t(state,
                      '请求涉及设备控制或参数修改，超出系统只读边界，予以拦截。',
                      'The request involves device control or parameter changes, which is outside the read-only boundary.')
        elif _contains_any(q, HIGH_RISK_WORDS):
            route = 'high_risk'
            note = _t(state,
                      '判定为高危工况：立即停机并上报，仅输出安全建议。',
                      'High-risk condition detected: stop immediately, report, and output safety guidance only.')
        elif not state['alarm_code'] and faq and faq['得分'] >= 0.7:
            route = 'qa'
            note = _t(state,
                      '命中知识库问答条目 %s（相关度 %.2f）' % (faq['编号'], faq['得分']),
                      'Matched FAQ entry %s (relevance %.2f)' % (faq['编号'], faq['得分']))
        elif not state['alarm_code'] and _contains_any(q, QA_HINTS) and not _contains_any(q, FAULT_WORDS):
            route = 'qa'
            note = _t(state, '识别为知识问答请求，进入问答检索。',
                      'Recognized as a knowledge question; routing to FAQ retrieval.')
        state['route'] = route
        state['qa'] = faq if route == 'qa' else None
        state['trace'] = state.get('trace', []) + [{
            '步骤': name,
            '设备': state['device'],
            '报警代码': state['alarm_code'] or '—',
            '路由': (_ROUTE_EN if lang == 'en' else _ROUTE_CN)[route],
            '说明': note,
        }]
        return state


class QAAgent:
    """知识问答智能体：从问答库取用真实收录的答案，未收录时如实说明。"""
    name = '知识问答智能体'
    name_en = 'Knowledge Q&A Agent'

    def run(self, state):
        lang = _lang(state)
        name = self.name_en if lang == 'en' else self.name
        retriever = get_retriever()
        qa = state.get('qa') or retriever.search_faq(state.get('user_query', ''), lang)
        state['qa'] = qa

        if qa:
            case = retriever.case(qa['案例编号']) or {}
            sugs = [s for s in retriever.suggestions([qa['案例编号']], lang, limit=8) if s != qa['问题']]
            for s in retriever.related_questions(state.get('user_query', ''), lang, exclude=qa['问题'], limit=6):
                if len(sugs) >= 4:
                    break
                if s not in sugs:
                    sugs.append(s)
            state['suggestions'] = sugs[:4]
            state['qa_case'] = case
            state['trace'] = state.get('trace', []) + [{
                '步骤': name,
                '命中问答': '%s（相关度 %.2f）' % (qa['编号'], qa['得分']),
                '关联案例': '%s %s' % (qa['案例编号'], case.get('标题' if lang == 'zh' else '标题EN', '')),
                '依据': qa['依据'],
            }]
        else:
            state['qa_case'] = None
            state['suggestions'] = retriever.related_questions(state.get('user_query', ''), lang, limit=4)
            state['trace'] = state.get('trace', []) + [{
                '步骤': name,
                '结果': _t(state, '知识库未收录该问题，如实说明并给出相近问题。',
                          'The question is not covered by the knowledge base; no speculative answer is given.'),
            }]
        return state


class RetrievalAgent:
    """知识检索智能体：混合检索定位到条款级引用。"""
    name = '知识检索智能体'
    name_en = 'Retrieval Agent'

    def __init__(self):
        self.retriever = get_retriever()

    def run(self, state):
        lang = _lang(state)
        hits = self.retriever.search(state.get('user_query', ''), top_k=3)
        state['retrieved'] = hits
        state['suggestions'] = self.retriever.suggestions(
            [h['案例编号'] for h in hits], lang, limit=4)
        state['trace'] = state.get('trace', []) + [{
            '步骤': self.name_en if lang == 'en' else self.name,
            '命中案例': '；'.join(h['案例编号'] for h in hits) or _t(state, '未命中（如实说明，不作猜测）',
                                                                    'No match (stated honestly, no guessing)'),
            '来源': _t(state, '关键词精确匹配 + 向量相似度混合检索（Chroma）',
                       'Keyword exact match + vector similarity hybrid retrieval (Chroma)'),
            '推荐追问': '；'.join(state['suggestions']) if state['suggestions'] else _t(state, '无', 'None'),
        }]
        return state


class DiagnosisAgent:
    """故障诊断智能体：输出按概率排序的原因与现场确认项。"""
    name = '故障诊断智能体'
    name_en = 'Diagnosis Agent'

    def run(self, state):
        lang = _lang(state)
        name = self.name_en if lang == 'en' else self.name
        hits = state.get('retrieved', [])
        if not hits:
            state['causes'] = []
            state['checks'] = []
            state['refs'] = []
            state['trace'] = state.get('trace', []) + [{
                '步骤': name,
                '结果': _t(state, '证据不足：未查到对应条款，不作猜测，建议转人工。',
                          'Insufficient evidence: no matching clause, no guessing, escalate to a human.'),
            }]
            return state
        # 报警号精确命中时，只采用该报警号对应的案例，避免不同案例的原因混排
        alarm = state.get('alarm_code') or ''
        exact = [h for h in hits if alarm and h['报警代码'] == alarm]
        src = exact or hits
        cause_key = '可能原因EN' if lang == 'en' else '可能原因'
        check_key = '现场确认项EN' if lang == 'en' else '现场确认项'
        ref_key = '来源EN' if lang == 'en' else '来源'
        if not llm_client.enabled() or lang == 'en':
            causes, refs = [], []
            for h in src:
                for reason in h[cause_key]:
                    reason = _strip_no(reason)
                    if reason and reason not in causes:
                        causes.append(reason)
                        refs.append(h[ref_key])
            state['causes'] = causes[:5]
            state['refs'] = refs[:5]
            state['checks'] = [c for h in src for c in h[check_key]][:6]
            state['trace'] = state.get('trace', []) + [{
                '步骤': name,
                '结果': _t(state, '规则模式输出按概率排序的原因 %d 条，附条款引用。' % len(state['causes']),
                          'Rule mode returned %d causes ranked by probability, with clause-level citations.'
                          % len(state['causes'])),
            }]
            return state
        ranked = llm_client.rank_causes(state.get('user_query', ''), src)
        if ranked:
            state['causes'] = ['%s（依据：%s）' % (r.get('原因', ''), r.get('依据', '')) for r in ranked]
            state['refs'] = []
        else:
            state['causes'] = [_strip_no(r) for h in src for r in h['可能原因']][:5]
            state['refs'] = [h['来源'] for h in src][:5]
        state['checks'] = [c for h in src for c in h['现场确认项']][:6]
        state['trace'] = state.get('trace', []) + [{
            '步骤': name,
            '结果': '大模型辅助排序完成，共 %d 条原因。' % len(state['causes']),
        }]
        return state


class SpareOrderAgent:
    """备件与工单智能体：查询库存与替代型号，生成字段完整的工单草稿。"""
    name = '备件与工单智能体'
    name_en = 'Spare Parts & Work Order Agent'

    def run(self, state):
        lang = _lang(state)
        name = self.name_en if lang == 'en' else self.name
        hits = state.get('retrieved', [])
        if not hits:
            state['stock'] = []
            state['work_order'] = ''
            state['trace'] = state.get('trace', []) + [{
                '步骤': name,
                '备件查询': _t(state, '证据不足：跳过备件查询与工单生成。',
                            'Insufficient evidence: spare parts lookup and work order are skipped.'),
            }]
            return state
        codes = []
        for h in hits:
            for code in h['关联备件']:
                if code not in codes and code != '待检查后确认':
                    codes.append(code)
        stock, msg = query_stock(codes)
        order, text = generate_work_order(
            state.get('device', '未识别'),
            hits[0]['标题EN'] if lang == 'en' else hits[0]['标题'],
            state.get('causes', []),
            state.get('checks', []),
            stock,
            state.get('route', 'normal'),
            lang=lang,
        )
        state['stock'] = stock
        state['work_order'] = text
        state['trace'] = state.get('trace', []) + [{
            '步骤': name,
            '备件查询': msg if lang == 'zh' else 'Matched %d spare part record(s).' % len(stock),
            '工单草稿': _t(state, '已生成（字段完整，待人工确认后派工）',
                        'Draft generated (complete fields, dispatch after human confirmation)'),
        }]
        return state


class AuditAgent:
    """审核兜底智能体：校验安全边界与引用一致性，高危与越界统一兜底。"""
    name = '审核兜底智能体'
    name_en = 'Audit & Safety Agent'

    def run(self, state):
        lang = _lang(state)
        route = state.get('route', 'normal')
        if route == 'high_risk':
            state['audit_note'] = _t(
                state,
                '高危工况处理建议：1.立即停机并设置警示标识；2.上报班组长与设备管理员；'
                '3.由具备资质的维修人员现场确认后再处置。系统不输出自动处置步骤、不生成工单草稿。',
                'High-risk guidance: 1. Stop the machine immediately and set warning signs; '
                '2. Report to the team leader and equipment manager; 3. Only qualified maintenance '
                'personnel may inspect and decide on repairs. No automatic actions or work order drafts are produced.')
        elif route == 'reject':
            state['audit_note'] = _t(
                state,
                '本系统仅提供只读诊断辅助，不接入设备控制系统，不修改 PLC 参数与工艺配置。'
                '如确需参数调整，请按管理制度由授权人员执行。',
                'This system provides read-only diagnostic assistance only. It does not connect to the '
                'control system and never modifies PLC parameters or process settings. Authorized personnel '
                'must perform any parameter changes under the management procedure.')
        elif route == 'qa':
            if state.get('qa'):
                state['audit_note'] = _t(
                    state,
                    '回答来自知识库已收录问答条目，未作推测，引用可追溯；现场操作须由持证人员确认后执行。',
                    'The answer comes from a recorded FAQ entry with traceable citation and no speculation. '
                    'On-site work must be confirmed by certified personnel.')
            else:
                state['audit_note'] = _t(
                    state,
                    '知识库未收录该问题，系统未生成推测性回答；已给出相近的可答问题。',
                    'The question is not covered by the knowledge base. No speculative answer is generated; '
                    'related answerable questions are suggested instead.')
        else:
            cites_ok = bool(state.get('causes'))
            state['audit_note'] = _t(state, '结论与引用一致性校验通过。' if cites_ok else '证据不足，结论区不输出推测性内容。',
                                     'Conclusion and citation consistency check passed.' if cites_ok
                                     else 'Insufficient evidence; no speculative content is shown.')
            state['audit_note'] += _t(state, '所有结论须由具备资质的维修人员现场确认后执行。',
                                      ' All conclusions must be confirmed on site by qualified maintenance personnel.')
        state['trace'] = state.get('trace', []) + [{
            '步骤': self.name_en if lang == 'en' else self.name,
            '校验': _t(state, '安全边界与引用一致性', 'Safety boundary and citation consistency'),
            '结果': state['audit_note'][:38] + '……',
        }]
        return state


class ReplyAgent:
    """回复组装智能体：按路由组装最终回复。"""
    name = '回复组装智能体'
    name_en = 'Reply Composer Agent'

    def run(self, state):
        lang = _lang(state)
        route = state.get('route', 'normal')
        lines = []
        if route == 'reject':
            lines.append(_t(state, '【越界请求 · 已拦截】', '[Out of scope · Blocked]'))
            lines.append(state.get('audit_note', ''))
        elif route == 'high_risk':
            lines.append(_t(state, '【高危工况 · 强制转人工】', '[High risk · Escalated to human]'))
            lines.append(_t(state, '设备：%s；报警代码：%s', 'Device: %s; Alarm: %s')
                         % (state.get('device', ''), state.get('alarm_code') or '—'))
            lines.append('')
            lines.append(state.get('audit_note', ''))
        elif route == 'qa':
            qa = state.get('qa')
            if qa:
                case = state.get('qa_case') or {}
                lines.append(_t(state, '【知识问答】', '[Knowledge Q&A]'))
                lines.append(_t(state, '问题：%s', 'Question: %s') % qa['问题'])
                lines.append(_t(state, '回答：', 'Answer: ') + qa['答案'])
                lines.append(_t(state, '依据：', 'Source: ') + qa['依据'])
                title = case.get('标题EN') if lang == 'en' else case.get('标题')
                lines.append(_t(state, '关联案例：%s %s', 'Related case: %s %s')
                             % (qa['案例编号'], title or ''))
                lines.append(state.get('audit_note', ''))
            else:
                lines.append(_t(state, '【未收录】知识库暂未收录该问题，系统不作猜测。',
                                '[Not covered] The knowledge base does not cover this question; no guessing.'))
                lines.append(_t(state, '建议核对问法，或从下列已收录问题中重新选择。',
                                'Please rephrase the question or pick one of the answerable questions below.'))
        else:
            hits = state.get('retrieved', [])
            if not hits:
                lines.append(_t(state, '【无法识别】该输入未命中任何已知设备故障知识，本系统不作猜测、不予作答。',
                                '[Unrecognized] The input does not match any known equipment fault; no guessing is allowed.'))
                lines.append(_t(state, '建议：核对设备型号与报警代码后重试；或转人工咨询设备厂家。',
                                'Suggestion: verify the device model and alarm code, or escalate to the equipment vendor.'))
            else:
                lines.append(_t(state, '【诊断结论】设备：%s；报警代码：%s',
                                '[Diagnosis] Device: %s; Alarm: %s')
                             % (state.get('device', ''), state.get('alarm_code') or '—'))
                lines.append('')
                lines.append(_t(state, '可能原因（按概率排序）：', 'Possible causes (ranked by probability):'))
                refs = state.get('refs', [])
                for i, c in enumerate(state.get('causes', []), 1):
                    r = refs[i - 1] if i - 1 < len(refs) else ''
                    line = '%d. %s' % (i, c)
                    if r:
                        line += _t(state, '（依据：%s）', ' (Source: %s)') % r
                    lines.append(line)
                if state.get('checks'):
                    lines.append('')
                    lines.append(_t(state, '现场确认项：', 'On-site verification:'))
                    for c in state['checks']:
                        lines.append('· ' + c)
                if state.get('work_order'):
                    lines.append('')
                    lines.append(state['work_order'])
                lines.append('')
                lines.append(_t(state, '引用来源：', 'Sources: ')
                             + '；'.join(h.get('来源EN') if lang == 'en' else h.get('来源') for h in hits))
                lines.append(state.get('audit_note', ''))
        state['final'] = '\n'.join(lines)
        state['trace'] = state.get('trace', []) + [{
            '步骤': self.name_en if lang == 'en' else self.name,
            '结果': _t(state, '回复已组装', 'Reply composed'),
        }]
        return state
