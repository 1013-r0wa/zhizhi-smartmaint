# -*- coding: utf-8 -*-
"""工具层：备件库存查询与维修工单草稿生成（模拟数据，只读）。"""
import csv
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STOCK = os.path.join(DATA_DIR, 'stock_sim.csv')


def load_stock():
    with open(STOCK, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def query_stock(keywords):
    """按备件编码或名称查询库存。未命中时明确说明，绝不编造。"""
    rows = load_stock()
    hits = []
    seen = set()
    for kw in keywords or []:
        for r in rows:
            if kw and (kw in r['part_code'] or kw in r['part_name']):
                key = r['part_code']
                if key not in seen:
                    seen.add(key)
                    hits.append(r)
    if not hits:
        return [], '未查到相关备件，请核实编码后重试或转人工。'
    return hits, '命中 %d 条备件记录。' % len(hits)


def generate_work_order(device, fault_type, causes, checks, parts, route, lang='zh'):
    """生成字段完整的维修工单草稿（待人工确认，不自动派工）。"""
    if lang == 'en':
        lines = ['[Maintenance Work Order Draft]']
        lines.append('Device: %s' % device)
        lines.append('Fault type: %s' % fault_type)
        lines.append('Possible causes: %s' % ('; '.join(causes[:3]) or 'To be confirmed'))
        lines.append('On-site verification: %s' % ('; '.join(checks) or 'To be confirmed'))
        parts_text = '; '.join(
            '%s %s (qty %s, bin %s)' % (p['part_code'], p.get('part_name_en') or p['part_name'],
                                        p['qty'], p['location'])
            for p in parts
        )
        lines.append('Spare parts: %s' % (parts_text or 'None'))
        lines.append('Priority: %s' % ('Urgent' if route == 'high_risk' else 'Normal'))
        lines.append('Status: Awaiting human confirmation before dispatch')
        lines.append('Generated: %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
        return None, '\n'.join(lines)

    lines = ['【维修工单草稿】']
    lines.append('设备编号：%s' % device)
    lines.append('故障类别：%s' % fault_type)
    lines.append('可能原因：%s' % ('；'.join(causes[:3]) or '待确认'))
    lines.append('现场确认项：%s' % ('；'.join(checks) or '待确认'))
    parts_text = '；'.join(
        '%s %s（库存%s，库位%s）' % (p['part_code'], p['part_name'], p['qty'], p['location'])
        for p in parts
    )
    lines.append('关联备件：%s' % (parts_text or '无'))
    lines.append('优先级：%s' % ('紧急' if route == 'high_risk' else '普通'))
    lines.append('工单状态：待人工确认后派工')
    lines.append('生成时间：%s' % time.strftime('%Y-%m-%d %H:%M:%S'))
    return None, '\n'.join(lines)
