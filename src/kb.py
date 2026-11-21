# -*- coding: utf-8 -*-
"""知识库加载与混合检索：关键词精确匹配 + 向量相似度，离线可用。"""
import hashlib
import math
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
KB_FILE = os.path.join(DATA_DIR, 'equipment_kb.md')
FAQ_FILE = os.path.join(DATA_DIR, 'faq.md')

_WORD_RE = re.compile(r'[\u4e00-\u9fff]|[A-Za-z0-9\-]+')


def _tokens(text):
    return set(_WORD_RE.findall((text or '').lower()))


def _hash_embed(text, dim=256):
    vec = [0.0] * dim
    for w in _WORD_RE.findall((text or '').lower()):
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def _cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def _grams(text):
    """中文字符二元组 + 英文/数字词，用于问句匹配。"""
    s = (text or '').lower()
    chars = re.findall(r'[\u4e00-\u9fff]', s)
    grams = set(re.findall(r'[a-z0-9]+', s))
    grams.update(chars)
    for i in range(len(chars) - 1):
        grams.add(chars[i] + chars[i + 1])
    return grams


def _split(text):
    return [s.strip() for s in re.split(r'[;；]', text or '') if s.strip()]


def _case_text(c):
    return (c['标题'] + c['标题EN'] + c['现象'] + c['现象EN'] + c['设备'] + c['设备EN'] + c['报警代码']
            + ' '.join(c['可能原因']) + ' '.join(c['可能原因EN'])
            + ' '.join(c['现场确认项']) + ' '.join(c['现场确认项EN'])
            + ' '.join(c['关联备件']))


def _read_sections(path):
    """按 `## 编号 标题` 分段读取 `- 键：值` 字段。"""
    sections, cur = [], None
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('## '):
                if cur:
                    sections.append(cur)
                head = line[3:].strip()
                code, _, title = head.partition(' ')
                cur = {'_编号': code.strip(), '_标题': title.strip()}
                continue
            if line.startswith('- ') and cur is not None:
                body = line[2:].strip()
                key, sep, value = body.partition('：')
                if not sep:
                    key, sep, value = body.partition(':')
                if sep:
                    cur[key.strip()] = value.strip()
    if cur:
        sections.append(cur)
    return sections


def load_cases(path=KB_FILE):
    result = []
    for c in _read_sections(path):
        result.append({
            '案例编号': c.get('案例编号') or c.get('_编号', ''),
            '标题': c.get('_标题', ''),
            '标题EN': c.get('标题EN', ''),
            '报警代码': c.get('报警代码', ''),
            '设备': c.get('设备', ''),
            '设备EN': c.get('设备EN', ''),
            '现象': c.get('现象', ''),
            '现象EN': c.get('现象EN', ''),
            '可能原因': _split(c.get('可能原因', '')),
            '可能原因EN': _split(c.get('可能原因EN', '')),
            '现场确认项': _split(c.get('现场确认项', '')),
            '现场确认项EN': _split(c.get('现场确认项EN', '')),
            '关联备件': [s.strip() for s in re.split(r'[、,]', c.get('关联备件', '')) if s.strip()],
            '关联备件EN': c.get('关联备件EN', ''),
            '来源': c.get('来源', ''),
            '来源EN': c.get('来源EN', ''),
            '高危': (c.get('高危', '否') == '是'),
        })
    return result


def load_faqs(path=FAQ_FILE):
    result = []
    for f in _read_sections(path):
        result.append({
            '编号': f.get('_编号', ''),
            '问题': f.get('_标题', ''),
            '问题EN': f.get('问题EN', ''),
            '所属案例': f.get('所属案例', ''),
            '答案': f.get('答案', ''),
            '答案EN': f.get('答案EN', ''),
            '依据': f.get('依据', ''),
            '依据EN': f.get('依据EN', ''),
        })
    return result


class HybridRetriever:
    """关键词精确匹配与向量相似度两路检索，合并重排后输出带引用案例。"""

    def __init__(self):
        self.cases = load_cases()
        self.faqs = load_faqs()
        self._chroma = None
        self._faq_docs = []
        for f in self.faqs:
            case = self.case(f['所属案例']) or {}
            f['_grams'] = _grams(' '.join([
                f['问题'], f['问题EN'], f['答案'], f['答案EN'],
                case.get('标题', ''), case.get('标题EN', ''),
            ]))
            f['_vec'] = _hash_embed(' '.join([f['问题'], f['问题EN'], f['答案'], f['答案EN']]))
            self._faq_docs.append(f)
        try:
            import chromadb
            client = chromadb.Client()
            col = client.get_or_create_collection('zhizhi_kb', metadata={'hnsw:space': 'cosine'})
            ids = [c['案例编号'] for c in self.cases]
            existing = col.get(include=[])
            if ids and not existing.get('ids'):
                col.add(
                    ids=ids,
                    embeddings=[_hash_embed(_case_text(c)) for c in self.cases],
                    documents=[c['标题'] + '：' + c['现象'] for c in self.cases],
                )
            self._chroma = col
        except Exception:
            self._chroma = None

    def case(self, case_id):
        for c in self.cases:
            if c['案例编号'] == case_id:
                return c
        return None

    def search(self, query, top_k=3):
        q = query or ''
        tokens = _tokens(q)
        kw = {}
        alarm_hit = {}
        for c in self.cases:
            overlap = len(tokens & _tokens(_case_text(c)))
            kw[c['案例编号']] = overlap * 10.0
            alarm_hit[c['案例编号']] = bool(c['报警代码'] and c['报警代码'].upper() in q.upper())
        vec = {}
        if self._chroma is not None:
            try:
                res = self._chroma.query(
                    query_embeddings=[_hash_embed(q)],
                    n_results=len(self.cases),
                    include=['distances'],
                )
                for idx, cid in enumerate(res.get('ids', [[]])[0]):
                    d = res.get('distances', [[1.0]])[0][idx]
                    vec[cid] = max(0.0, 1.0 - d) * 5.0
            except Exception:
                pass
        picked = []
        for c in self.cases:
            cid = c['案例编号']
            # 相关性硬门槛：报警号精确命中，或关键词重合足够高，或向量相似度达标
            relevant = alarm_hit[cid] or kw[cid] >= 30.0 or vec.get(cid, 0.0) >= 3.0
            if relevant:
                total = kw[cid] + (50.0 if alarm_hit[cid] else 0.0) + vec.get(cid, 0.0)
                picked.append((total, c))
        picked.sort(key=lambda x: x[0], reverse=True)
        result = []
        for total, c in picked[:top_k]:
            d = dict(c)
            if alarm_hit[c['案例编号']]:
                d['命中方式'] = '报警号精确匹配'
            elif vec.get(c['案例编号'], 0.0) >= 3.0:
                d['命中方式'] = '关键词+向量'
            else:
                d['命中方式'] = '关键词'
            result.append(d)
        # 无任何相关案例时返回空，由诊断与审核环节如实声明、不作猜测
        return result

    def suggestions(self, case_ids, lang='zh', limit=4):
        """推荐追问：只返回问答库中真实收录、可给出答案的问题。"""
        ids = set(case_ids or [])
        out = []
        for f in self.faqs:
            if f['所属案例'] in ids:
                q = f['问题EN'] if lang == 'en' else f['问题']
                if q and q not in out:
                    out.append(q)
            if len(out) >= limit:
                break
        return out

    def search_faq(self, query, lang='zh'):
        """问答检索：字符二元组覆盖率 + 向量余弦，返回最佳问答条目。"""
        q = (query or '').strip()
        if not q:
            return None
        qg = _grams(q)
        qv = _hash_embed(q)
        best, best_score = None, 0.0
        for f in self._faq_docs:
            if not qg or not f['_grams']:
                continue
            coverage = len(qg & f['_grams']) / float(len(qg))
            cos = _cosine(qv, f['_vec'])
            score = 0.75 * coverage + 0.25 * cos
            if score > best_score:
                best, best_score = f, score
        if best is None or best_score < 0.45:
            return None
        return {
            '编号': best['编号'],
            '问题': best['问题EN'] if lang == 'en' else best['问题'],
            '答案': best['答案EN'] if lang == 'en' else best['答案'],
            '依据': best['依据EN'] if lang == 'en' else best['依据'],
            '案例编号': best['所属案例'],
            '得分': round(best_score, 3),
        }

    def related_questions(self, query, lang='zh', exclude=None, limit=4):
        """未命中时给出相近的可答问题，避免答非所问。"""
        qg = _grams(query or '')
        qv = _hash_embed(query or '')
        ranked = []
        for f in self._faq_docs:
            text = f['问题EN'] if lang == 'en' else f['问题']
            if text == exclude:
                continue
            coverage = len(qg & f['_grams']) / float(len(qg) or 1)
            score = 0.75 * coverage + 0.25 * _cosine(qv, f['_vec'])
            ranked.append((score, text))
        ranked.sort(key=lambda x: x[0], reverse=True)
        out = []
        for _, text in ranked:
            if text and text not in out:
                out.append(text)
            if len(out) >= limit:
                break
        return out


_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever
