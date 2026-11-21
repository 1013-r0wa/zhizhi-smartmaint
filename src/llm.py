# -*- coding: utf-8 -*-
"""大模型网关（可选）：未配置 API Key 或 SM_OFFLINE=1 时自动停用。"""
import json
import os

from dotenv import load_dotenv


def enabled():
    load_dotenv()
    key = os.getenv('LLM_API_KEY', '').strip()
    return bool(key and not os.getenv('SM_OFFLINE'))


def _client():
    if not enabled():
        return None
    try:
        from openai import OpenAI
        base = os.getenv('LLM_BASE_URL', '').strip() or None
        model = os.getenv('LLM_MODEL', '').strip() or 'deepseek-chat'
        return OpenAI(api_key=os.getenv('LLM_API_KEY', '').strip(), base_url=base), model
    except Exception:
        return None


def rank_causes(query, cases, top_k=3):
    """大模型辅助原因排序；失败返回 None，由调用方回退规则排序。"""
    if not enabled():
        return None
    c = _client()
    if not c:
        return None
    client, model = c
    try:
        payload = [{'案例编号': x['案例编号'], '标题': x['标题'], '可能原因': x['可能原因']} for x in cases]
        prompt = (
            '你是车间设备故障诊断辅助智能体。仅可基于以下知识库案例重新排序可能原因，'
            '不得编造知识库之外的原因。只输出 JSON 数组，每项含“原因”与“依据”字段。\n'
            '用户描述：%s\n知识库案例：%s' % (query, json.dumps(payload, ensure_ascii=False))
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1,
        )
        text = resp.choices[0].message.content
        start, end = text.find('['), text.rfind(']')
        if start < 0 or end <= start:
            return None
        data = json.loads(text[start:end + 1])
        if isinstance(data, list) and data:
            return data[:top_k]
        return None
    except Exception:
        return None
