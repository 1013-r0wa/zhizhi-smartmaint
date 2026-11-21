# -*- coding: utf-8 -*-
"""智维（SmartMaint）原型演示入口：Streamlit 前端。"""
import html
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# 云端部署：把 Streamlit Secrets 中的配置注入环境变量，供 src/llm.py 统一读取
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)
except Exception:
    pass

from src import llm as llm_client
from src.graph import build_graph
from src.kb import get_retriever
from src.tools import load_stock

st.set_page_config(
    page_title='智维 · 车间设备故障诊断与维修协同智能体',
    layout='wide',
    initial_sidebar_state='auto',
)

if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = '中文'
LANG = 'en' if st.session_state.lang_choice == 'English' else 'zh'


def T(zh, en):
    return en if LANG == 'en' else zh


LLM_ON = llm_client.enabled()
RETRIEVER = get_retriever()
STOCK = load_stock()


def _has_code(case):
    return bool(case.get('报警代码')) and case['报警代码'] not in ('无', '—', '无代码')


ALARM_CNT = len({c['报警代码'] for c in RETRIEVER.cases if _has_code(c)})

EXAMPLES = [
    ('主轴温度过高', 'Spindle overheating',
     'M-003 主轴电机温度过高，报警 ALM-2041，请帮我看看怎么处理。',
     'M-003 spindle motor is overheating, alarm ALM-2041. How should I handle it?'),
    ('刀库换刀超时', 'Tool change timeout',
     'M-011 加工中心刀库换刀超时，报警 ALM-4102。',
     'M-011 machining center tool magazine tool change times out, alarm ALM-4102.'),
    ('液压压力低', 'Low hydraulic pressure',
     'M-008 液压站压力低，报警 ALM-3105，油压上不去。',
     'M-008 hydraulic station pressure is low, alarm ALM-3105, pressure cannot build up.'),
    ('高危 · 剧烈抖动', 'High risk · vibration',
     'M-003 主轴运行时剧烈抖动并伴随异响，疑似机械崩裂风险。',
     'M-003 spindle vibrates severely with abnormal noise and suspected mechanical fracture risk.'),
    ('越界 · 修改参数', 'Out of scope · PLC',
     '帮我把 M-003 的 PLC 参数改一下，直接远程启动主轴。',
     'Please change the PLC parameters of M-003 and start the spindle remotely.'),
]

PAPERS = [
    {
        'title': 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
        'authors': 'Patrick Lewis, Ethan Perez, Aleksandra Piktus, et al.',
        'venue': 'NeurIPS 2020', 'id': 'arXiv:2005.11401',
        'url': 'https://arxiv.org/abs/2005.11401',
        'why_zh': '检索增强生成：用外部知识约束生成，显著降低幻觉，与本项目“条款级引用”的设计一致。',
        'why_en': 'RAG grounds generation in external knowledge and reduces hallucination, matching our clause-level citation design.',
    },
    {
        'title': 'ReAct: Synergizing Reasoning and Acting in Language Models',
        'authors': 'Shunyu Yao, Jeffrey Zhao, Dian Yu, et al.',
        'venue': 'ICLR 2023', 'id': 'arXiv:2210.03629',
        'url': 'https://arxiv.org/abs/2210.03629',
        'why_zh': '推理与行动交替的智能体范式，为分诊、检索、诊断的条件路由提供方法参考。',
        'why_en': 'An agent paradigm that interleaves reasoning and action, informing our conditional routing across triage, retrieval and diagnosis.',
    },
    {
        'title': 'Chain-of-Thought Prompting Elicits Reasoning in Large Language Models',
        'authors': 'Jason Wei, Xuezhi Wang, Dale Schuurmans, et al.',
        'venue': 'NeurIPS 2022', 'id': 'arXiv:2201.11903',
        'url': 'https://arxiv.org/abs/2201.11903',
        'why_zh': '思维链提示提升复杂推理的可解释性，对应本项目按概率排序、逐项确认的诊断结构。',
        'why_en': 'Chain-of-thought prompting improves the interpretability of complex reasoning, reflected in our probability-ranked, checklist-based diagnosis.',
    },
    {
        'title': 'AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation',
        'authors': 'Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al.',
        'venue': 'arXiv 2023', 'id': 'arXiv:2308.08155',
        'url': 'https://arxiv.org/abs/2308.08155',
        'why_zh': '多智能体协作框架，与 LangGraph 编排六个角色、共享状态的设计形成对照。',
        'why_en': 'A multi-agent collaboration framework that parallels our LangGraph orchestration of six roles sharing one state.',
    },
    {
        'title': 'Machinery health prognostics: A systematic review from data acquisition to RUL prediction',
        'authors': 'Yaguo Lei, Naipeng Li, Liang Guo, et al.',
        'venue': 'Mechanical Systems and Signal Processing, 2018', 'id': 'DOI: 10.1016/j.ymssp.2017.11.016',
        'url': 'https://doi.org/10.1016/j.ymssp.2017.11.016',
        'why_zh': '设备健康管理与剩余寿命预测的系统综述，为故障原因排序与预警阈值提供理论背景。',
        'why_en': 'A systematic review of machinery health prognostics and RUL prediction, providing background for cause ranking and warning thresholds.',
    },
    {
        'title': 'Cloud-enabled prognosis for manufacturing',
        'authors': 'Robert X. Gao, Lihui Wang, Roberto Teti, et al.',
        'venue': 'CIRP Annals, 2015', 'id': 'DOI: 10.1016/j.cirp.2015.05.004',
        'url': 'https://doi.org/10.1016/j.cirp.2015.05.004',
        'why_zh': '面向制造的云化预测性维护架构，对应本项目“车间现场 + 云端知识库”的部署形态。',
        'why_en': 'A cloud-enabled prognostics architecture for manufacturing, mirroring our “shop floor plus cloud knowledge base” deployment.',
    },
]

CSS = """
<style>
:root{--zv-brand:#0E7490;--zv-ink:#16283B;--zv-muted:#7B8CA0;--zv-line:#E6EDF5;--zv-bg:#F4F7FB}
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.stApp{background:var(--zv-bg)}
.block-container{max-width:1180px;padding-top:1.2rem;padding-bottom:2rem}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbar"]{background:transparent}
[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"]{display:none}
[data-testid="stExpandSidebarButton"]{background:#fff !important;border:1px solid var(--zv-line) !important;
  border-radius:9px;box-shadow:0 4px 14px rgba(18,44,72,.12);width:36px;height:32px}
[data-testid="stExpandSidebarButton"]:hover{border-color:var(--zv-brand) !important}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--zv-line)}

/* 顶部主视觉 */
.zv-hero{position:relative;overflow:hidden;border-radius:20px;padding:28px 32px 26px;color:#fff;
  background:radial-gradient(120% 140% at 88% 0%,rgba(56,214,196,.45) 0%,rgba(56,214,196,0) 55%),
  linear-gradient(115deg,#082A47 0%,#0F3F63 52%,#0B5F62 100%);
  box-shadow:0 18px 40px rgba(11,45,75,.22);margin-bottom:16px}
.zv-hero:after{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),
  linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:30px 30px}
.zv-hero-inner{position:relative;z-index:2;max-width:920px}
.zv-eyebrow{font-size:11.5px;letter-spacing:.22em;color:#8CE3D4;font-weight:700;margin-bottom:10px}
.zv-title{font-size:clamp(23px,3vw,34px);font-weight:800;line-height:1.3}
.zv-desc{margin-top:10px;font-size:13.5px;line-height:1.75;color:rgba(255,255,255,.8)}
.zv-badges{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px}
.zv-badges span{font-size:12px;padding:5px 12px;border-radius:999px;background:rgba(255,255,255,.10);
  border:1px solid rgba(255,255,255,.22);color:#E8F6F5}

/* 指标卡 */
.zv-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.zv-stat{background:#fff;border:1px solid var(--zv-line);border-radius:14px;padding:14px 16px;
  box-shadow:0 6px 16px rgba(18,44,72,.05)}
.zv-stat .v{font-size:22px;font-weight:800;color:#0F3D63;line-height:1.25}
.zv-stat .l{font-size:12.5px;font-weight:600;color:#3D5165;margin-top:2px}
.zv-stat .n{font-size:11.5px;color:#8595A8;margin-top:2px}

/* 区块标题 */
.zv-sec{display:flex;align-items:center;gap:10px;margin:1.35rem 0 .55rem}
.zv-no{font-size:11px;font-weight:700;color:var(--zv-brand);background:#E3F3F6;
  border:1px solid #C9EAEF;border-radius:6px;padding:2px 7px}
.zv-sec-t{font-size:16px;font-weight:700;color:var(--zv-ink)}
.zv-sec-d{font-size:12px;color:#8494A7}
.zv-chip-label{font-size:12px;color:var(--zv-muted);margin:12px 0 6px;font-weight:600}

/* 卡片与按钮 */
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-radius:16px !important;
  border:1px solid var(--zv-line) !important;box-shadow:0 8px 22px rgba(18,44,72,.06)}
.stButton>button{border-radius:10px;font-weight:600;border:1px solid #DCE5EF;color:#24405C;
  transition:all .15s ease;height:auto;min-height:2.55rem;padding:.45rem .9rem;white-space:normal}
.stButton>button [data-testid="stMarkdownContainer"] p{white-space:normal;overflow:visible;
  text-overflow:clip;line-height:1.35;font-size:12.5px}
.stButton>button:hover{border-color:var(--zv-brand);color:var(--zv-brand);background:#F2FAFB}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"]{background:linear-gradient(120deg,#0E7490,#0F766E);
  border:none;color:#fff;box-shadow:0 10px 20px rgba(14,116,144,.24)}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover{filter:brightness(1.06);color:#fff}
.stDownloadButton>button{border-radius:10px;font-weight:600;border:1px solid #DCE5EF;color:#24405C;
  height:auto;min-height:2.55rem}
.stTextArea textarea{border-radius:12px;font-size:14px;line-height:1.7;border:1px solid #DCE5EF;background:#FBFDFF}
.stTextArea textarea:focus{border-color:var(--zv-brand);box-shadow:0 0 0 3px rgba(14,116,144,.12)}

/* 状态提示条 */
.zv-alert{display:flex;gap:12px;align-items:flex-start;border-radius:14px;padding:14px 18px;
  border:1px solid;margin:.3rem 0 .9rem}
.zv-alert .zv-ico{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:13px;font-weight:800;color:#fff;flex:0 0 auto;background:#0F766E}
.zv-alert .zv-ico::after{content:"!"}
.zv-alert.ok{background:#EAF7F4;border-color:#BFE8DF;color:#0B5D52}
.zv-alert.ok .zv-ico::after{content:"\\2713"}
.zv-alert.warn{background:#FFF6E5;border-color:#F3D9A4;color:#8A5A0B}
.zv-alert.warn .zv-ico{background:#B45309}
.zv-alert.danger{background:#FDEEEE;border-color:#F3C6C6;color:#9B1C1C}
.zv-alert.danger .zv-ico{background:#B91C1C}
.zv-alert.info{background:#EDF3FB;border-color:#CBDDF2;color:#1D4E89}
.zv-alert.info .zv-ico{background:#1D4E89}
.zv-alert.info .zv-ico::after{content:"i"}
.zv-alert .t{font-weight:700;font-size:15px}
.zv-alert .d{font-size:12.5px;opacity:.85;margin-top:3px;line-height:1.6}

/* 概要信息 */
.zv-tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 12px}
.zv-tile{background:#fff;border:1px solid var(--zv-line);border-radius:12px;padding:11px 14px;
  box-shadow:0 4px 12px rgba(18,44,72,.04)}
.zv-tile .k{font-size:11px;color:#8A9AAD;margin-bottom:3px}
.zv-tile .v{font-size:13.5px;font-weight:700;color:#1B3A57;line-height:1.4}

/* 卡片标题 */
.zv-card-title{font-size:13.5px;font-weight:700;color:var(--zv-ink);margin-bottom:6px;
  display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.zv-card-sub{font-size:11px;font-weight:400;color:#8A9AAD}

/* 原因列表 */
.zv-cause{padding:10px 0 12px;border-bottom:1px dashed #EDF2F8}
.zv-cause:last-child{border-bottom:none;padding-bottom:2px}
.zv-cause-row{display:flex;align-items:flex-start;gap:8px}
.zv-idx{flex:0 0 auto;width:20px;height:20px;border-radius:6px;background:#EAF3FA;color:#1D5C86;
  font-size:11.5px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
.zv-cause-text{flex:1;font-size:13.5px;line-height:1.6;color:#22374C}
.zv-pct{font-size:12px;font-weight:700;color:var(--zv-brand);background:#E7F4F6;
  border-radius:999px;padding:1px 8px;margin-top:2px;white-space:nowrap}
.zv-bar{height:6px;background:#EEF3F9;border-radius:999px;margin:8px 0 0 28px;overflow:hidden}
.zv-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#14B8A6,#0E7490)}
.zv-ref{font-size:11.5px;color:#8A9AAD;margin:6px 0 0 28px}

/* 现场确认项（可点击） */
[data-testid="stCheckbox"]{padding:1px 0}
[data-testid="stCheckbox"] label p{font-size:13px;line-height:1.6;color:#2A3D52}
.zv-confirm{margin-top:6px;padding:9px 12px;border-radius:10px;background:#EAF7F4;
  border:1px solid #BFE8DF;color:#0B5D52;font-size:12.5px;font-weight:600}

/* 库存数量与条目 */
.zv-qty{display:inline-block;min-width:26px;text-align:center;border-radius:999px;
  padding:1px 8px;font-size:11.5px;font-weight:700}
.zv-qty.ok{background:#E7F6F1;color:#0B6B54}
.zv-qty.zero{background:#FDECEC;color:#B42318}
.zv-inv-wrap{margin-top:4px}
.zv-inv{display:flex;align-items:center;justify-content:space-between;gap:8px;
  padding:8px 0;border-bottom:1px dashed #EDF2F8}
.zv-inv:last-child{border-bottom:none}
.zv-inv-name{font-size:12.5px;font-weight:600;color:#2A3D52}
.zv-inv-code{font-size:10.5px;color:#93A2B4;margin-top:2px;line-height:1.5}

/* 引用来源 */
.zv-src{padding:8px 0;border-bottom:1px dashed #EDF2F8}
.zv-src:last-child{border-bottom:none;padding-bottom:0}
.zv-src-top{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.zv-code{font-size:11px;font-weight:700;color:var(--zv-brand);background:#E7F4F6;
  border-radius:5px;padding:1px 7px}
.zv-src-title{font-size:13px;font-weight:600;color:#243B52}
.zv-src-meta{font-size:11.5px;color:#8A9AAD;margin-top:4px;line-height:1.5}

/* 问答结果 */
.zv-qa{background:#F8FCFB;border:1px solid #D9EFEA;border-radius:12px;padding:14px 16px}
.zv-qa-label{font-size:11px;font-weight:700;letter-spacing:.08em;color:#0E7490;margin-bottom:6px}
.zv-qa-text{font-size:14px;line-height:1.9;color:#233A4E}

/* 追问与审核说明 */
.zv-sug-title{font-size:13px;font-weight:700;color:var(--zv-ink);margin:16px 0 8px}
.zv-audit{margin-top:12px;font-size:12px;color:#6C7F93;background:#F7FAFD;
  border:1px dashed #DCE6F0;border-radius:10px;padding:10px 14px;line-height:1.65}
.zv-note{font-size:13.5px;line-height:1.85;color:#2A3D52}

/* 执行轨迹 */
.zv-timeline{position:relative;margin:4px 0 2px 8px;padding-left:22px;border-left:2px dashed #D7E2EE}
.zv-step{position:relative;padding-bottom:15px}
.zv-step:last-child{padding-bottom:2px}
.zv-dot{position:absolute;left:-34px;top:0;width:22px;height:22px;border-radius:50%;
  background:linear-gradient(135deg,#0E7490,#14B8A6);color:#fff;font-size:11px;font-weight:700;
  display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 4px #fff}
.zv-steptitle{font-weight:700;font-size:13.5px;color:var(--zv-ink)}
.zv-stepinfo{font-size:12.5px;color:#5F7489;margin-top:2px;line-height:1.65}

/* 底部功能区与论文 */
.zv-tool-label{font-size:11.5px;font-weight:700;color:#7B8CA0;letter-spacing:.04em;margin-bottom:4px}
.zv-tool-note{font-size:11.5px;color:#93A2B4;margin-top:4px;line-height:1.6}
.zv-papers{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.zv-paper{display:block;text-decoration:none !important;background:#fff;border:1px solid var(--zv-line);
  border-radius:14px;padding:14px 16px;transition:all .16s ease;box-shadow:0 4px 12px rgba(18,44,72,.04)}
.zv-paper:hover{border-color:#9FD8D2;box-shadow:0 10px 22px rgba(14,116,144,.12);transform:translateY(-1px)}
.zv-paper-top{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.zv-paper-venue{font-size:10.5px;font-weight:700;color:#0E7490;background:#E7F4F6;border-radius:5px;padding:2px 7px}
.zv-paper-id{font-size:10.5px;color:#9AA9BA;font-family:ui-monospace,Consolas,monospace}
.zv-paper-title{font-size:13.5px;font-weight:700;color:#1B3A57;line-height:1.5}
.zv-paper-authors{font-size:11px;color:#8A9AAD;margin-top:4px}
.zv-paper-why{font-size:12px;color:#5F7489;line-height:1.65;margin-top:8px;
  border-top:1px dashed #EDF2F8;padding-top:8px}
.zv-foot{margin-top:24px;padding-top:14px;border-top:1px solid var(--zv-line);
  font-size:11.5px;color:#93A2B4;line-height:1.7;text-align:center}

/* 右侧“我的”入口 */
.st-key-myfab{display:flex;justify-content:flex-end;margin:-2px 0 6px;z-index:60}
.st-key-myfab>[data-testid="stElementContainer"]{width:auto;margin-left:auto}
.st-key-myfab .stButton>button{border-radius:999px;padding:9px 20px;background:#fff;color:var(--zv-brand);
  border:1px solid #C9EAEF;font-weight:700;box-shadow:0 10px 24px rgba(14,116,144,.14)}
.st-key-myfab .stButton>button:hover{background:#F2FAFB;border-color:var(--zv-brand);color:var(--zv-brand)}
@media(min-width:1400px){
  .st-key-myfab{position:fixed;right:26px;top:104px;margin:0;width:auto;z-index:999990}
  .st-key-myfab .stButton>button{min-height:44px;padding:10px 22px}
}

/* “我的”工作台内部 */
.zv-my-head{border-radius:16px;padding:18px 20px 16px;color:#fff;position:relative;overflow:hidden;
  background:radial-gradient(130% 170% at 94% 0%,rgba(56,214,196,.5) 0%,rgba(56,214,196,0) 58%),
  linear-gradient(118deg,#0B3352 0%,#0F4C66 55%,#0E7490 100%);margin-bottom:14px}
.zv-my-eyebrow{font-size:10.5px;letter-spacing:.18em;font-weight:700;color:#8CE3D4}
.zv-my-title{font-size:20px;font-weight:800;margin-top:5px;line-height:1.35}
.zv-my-sub{font-size:12px;color:rgba(255,255,255,.78);margin-top:4px;line-height:1.65}
.zv-my-chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.zv-my-chip{font-size:11.5px;padding:4px 11px;border-radius:999px;background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.22);color:#EAF8F6}
.zv-rec-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.zv-rec-time{font-size:11px;color:#93A2B4}
.zv-rec-title{font-size:13.5px;font-weight:700;color:#1B3A57;line-height:1.55}
.zv-rec-meta{font-size:11.5px;color:#8A9AAD;margin-top:3px}
.zv-rec-prev{font-size:12px;color:#5F7489;line-height:1.7;margin-top:7px;padding-top:7px;
  border-top:1px dashed #EDF2F8;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.zv-empty{padding:26px 18px;text-align:center;background:#F7FAFD;border:1px dashed #DCE6F0;
  border-radius:12px;color:#6C7F93;font-size:12.5px;line-height:1.8}
.zv-empty b{display:block;font-size:14px;color:#1B3A57;margin-bottom:4px}
.zv-hist-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.zv-hist-sub{font-size:11.5px;color:#8A9AAD}
.zv-hist-empty{font-size:13px;color:#6C7F93;line-height:1.8;background:#F7FAFD;
  border:1px dashed #DCE6F0;border-radius:10px;padding:12px 14px}

/* 侧边栏 */
.zv-side-head{font-size:14px;font-weight:800;color:var(--zv-ink);margin:4px 0 4px}
.zv-side-head.sm{margin-top:20px}
.zv-side-sub{font-size:11.5px;color:#8A9AAD;margin-bottom:10px}
.zv-case{background:#fff;border:1px solid var(--zv-line);border-radius:11px;padding:9px 11px;margin-bottom:8px}
.zv-case-top{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.zv-case-title{font-size:12.5px;font-weight:600;color:#243B52;margin-top:4px}
.zv-case-dev{font-size:11px;color:#8A9AAD;margin-top:1px}
.zv-tag{font-size:10.5px;border-radius:5px;padding:1px 6px;background:#EEF3F9;color:#5B7186}
.zv-tag.danger{background:#FDECEC;color:#B42318}
.zv-tag.muted{background:#F2F5F9;color:#98A6B7}
.zv-mode{display:flex;gap:10px;align-items:flex-start;background:#F7FBF9;border:1px solid #DCEFE7;
  border-radius:11px;padding:10px 12px;margin-top:8px}
.zv-dot-mode{flex:0 0 auto;width:8px;height:8px;border-radius:50%;background:#12B76A;
  margin-top:6px;box-shadow:0 0 0 3px rgba(18,183,106,.15)}
.zv-dot-mode.off{background:#F79009;box-shadow:0 0 0 3px rgba(247,144,9,.15)}
.zv-mode-t{font-size:12.5px;font-weight:700;color:#1E4258}
.zv-mode-d{font-size:11px;color:#8A9AAD;margin-top:2px;line-height:1.5}
[data-testid="stExpander"] details{border:1px solid var(--zv-line);border-radius:14px;background:#fff}

@media(max-width:900px){
  .zv-stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .zv-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
  .zv-papers{grid-template-columns:1fr}
  .zv-hero{padding:22px 20px}
}
@media(max-width:640px){
  .block-container{padding-left:.9rem;padding-right:.9rem}
  .zv-sec{flex-wrap:wrap;row-gap:4px}
  .zv-sec-t{font-size:15px}
  .zv-sec-d{width:100%;font-size:11.5px}
  .zv-stat .v{font-size:19px}
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def _esc(value):
    return html.escape(str(value or ''))


def _case_title(case):
    """案例标题字段自带编号前缀，展示时去掉，避免与编号重复。"""
    title = (case.get('标题') or '').strip()
    code = (case.get('案例编号') or '').strip()
    if code and title.startswith(code):
        title = title[len(code):].strip()
    return title or code


def _sec(no, title, desc=''):
    return ('<div class="zv-sec"><span class="zv-no">%s</span><span class="zv-sec-t">%s</span>'
            '<span class="zv-sec-d">%s</span></div>' % (_esc(no), _esc(title), _esc(desc)))


def _banner(kind, title, desc):
    return ('<div class="zv-alert %s"><span class="zv-ico"></span><div><div class="t">%s</div>'
            '<div class="d">%s</div></div></div>' % (kind, _esc(title), _esc(desc)))


def _tiles(items):
    return '<div class="zv-tiles">' + ''.join(
        '<div class="zv-tile"><div class="k">%s</div><div class="v">%s</div></div>' % (_esc(k), _esc(v))
        for k, v in items) + '</div>'


def _parse_cause(text):
    """从原因文本中拆出概率，供进度条展示。"""
    pct = None
    m = re.search(r'[（(]\s*(?:probability|概率)\s*(\d+)\s*%\s*[）)]', text or '')
    if m:
        pct = int(m.group(1))
        text = (text[:m.start()] + text[m.end():]).strip()
    return (text or '').strip('；; '), pct


def _causes_html(causes, refs):
    out = []
    for i, c in enumerate(causes, 1):
        text, pct = _parse_cause(c)
        ref = refs[i - 1] if i - 1 < len(refs) else ''
        pct_html = '<span class="zv-pct">%d%%</span>' % pct if pct else ''
        bar = '<div class="zv-bar"><i style="width:%d%%"></i></div>' % pct if pct else ''
        ref_html = '<div class="zv-ref">%s：%s</div>' % (T('依据', 'Source'), _esc(ref)) if ref else ''
        out.append('<div class="zv-cause"><div class="zv-cause-row"><span class="zv-idx">%d</span>'
                   '<span class="zv-cause-text">%s</span>%s</div>%s%s</div>'
                   % (i, _esc(text), pct_html, bar, ref_html))
    return ''.join(out) or '<div class="zv-note">%s</div>' % T('暂无可展示的原因条目。', 'No causes to display.')


def _stock_list(rows):
    if not rows:
        return ('<div class="zv-note">%s</div>'
                % T('未查到相关备件，已如实说明，不编造库存。',
                    'No related spare parts found; stock is stated honestly, never fabricated.'))
    out = []
    for r in rows:
        try:
            qty = int(r.get('qty') or 0)
        except (TypeError, ValueError):
            qty = 0
        name = (r.get('part_name_en') or r.get('part_name')) if LANG == 'en' else r.get('part_name')
        loc = r.get('location') or '—'
        if LANG == 'en' and loc == '待采购':
            loc = 'To be procured'
        sub = r.get('substitute') or T('无', 'None')
        if LANG == 'en' and sub == '无':
            sub = 'None'
        out.append('<div class="zv-inv"><div><div class="zv-inv-name">%s</div>'
                   '<div class="zv-inv-code">%s · %s · %s %s</div></div>'
                   '<span class="zv-qty %s">%d</span></div>'
                   % (_esc(name), _esc(r.get('part_code')), _esc(loc), T('替代', 'Substitute'), _esc(sub),
                      'ok' if qty > 0 else 'zero', qty))
    return '<div class="zv-inv-wrap">' + ''.join(out) + '</div>'


def _sources_html(hits):
    out = []
    for h in hits:
        title = h.get('标题EN') if LANG == 'en' else _case_title(h)
        source = h.get('来源EN') if LANG == 'en' else h.get('来源')
        out.append('<div class="zv-src"><div class="zv-src-top"><span class="zv-code">%s</span>'
                   '<span class="zv-src-title">%s</span></div><div class="zv-src-meta">%s</div></div>'
                   % (_esc(h.get('案例编号')), _esc(title), _esc(source)))
    return ''.join(out)


TRACE_KEY_EN = {
    '步骤': 'Step', '设备': 'Device', '报警代码': 'Alarm', '路由': 'Route', '说明': 'Note',
    '命中案例': 'Cases', '来源': 'Source', '推荐追问': 'Follow-ups', '结果': 'Result',
    '备件查询': 'Spare parts', '工单草稿': 'Work order', '校验': 'Checks',
    '命中问答': 'FAQ hit', '关联案例': 'Related case', '依据': 'Source',
}


def _timeline_html(trace):
    rows = []
    for i, t in enumerate(trace, 1):
        step = t.get('步骤', '')
        info = ' · '.join('%s：%s' % (TRACE_KEY_EN.get(k, k) if LANG == 'en' else k, v)
                          for k, v in t.items() if k != '步骤' and v)
        rows.append('<div class="zv-step"><div class="zv-dot">%d</div><div class="zv-steptitle">%s</div>'
                    '<div class="zv-stepinfo">%s</div></div>' % (i, _esc(step), _esc(info)))
    return '<div class="zv-timeline">' + ''.join(rows) + '</div>'


def _pick(text):
    """快捷用例回调：在组件实例化前写入会话状态，避免报错。"""
    st.session_state.demo_query = text


def _ask(text):
    """推荐追问回调：填入问题并自动触发一次处理。"""
    st.session_state.demo_query = text
    st.session_state.auto_run = True


def _on_lang_change():
    # 切换语言后用同一问题重新处理，保证结果与界面语言一致
    if st.session_state.get('last_query'):
        st.session_state.auto_run = True
    # 语言控件在“我的”弹窗（fragment）内，需强制整页重跑才能更新主界面
    st.rerun(scope='app')


def _reset():
    for k in list(st.session_state.keys()):
        if k.startswith('chk_') or k in ('last_result', 'last_query', 'auto_run'):
            st.session_state.pop(k, None)
    st.session_state.demo_query = EXAMPLES[0][2] if LANG == 'zh' else EXAMPLES[0][3]


ROUTE_LABEL = {
    'normal': ('诊断', 'Diagnosis'),
    'qa': ('知识问答', 'Knowledge Q&A'),
    'high_risk': ('高危转人工', 'High-risk'),
    'reject': ('越界拦截', 'Out of scope'),
}


def _route_label(route):
    pair = ROUTE_LABEL.get(route or 'normal', ROUTE_LABEL['normal'])
    return pair[1] if LANG == 'en' else pair[0]


def _export_text(result):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    head = T('智维诊断记录', 'SmartMaint Record')
    lines = [
        '# %s' % head,
        '',
        '- %s: %s' % (T('生成时间', 'Generated at'), result.get('record_ts') or ts),
        '- %s: %s' % (T('问题', 'Question'), result.get('user_query', '')),
        '- %s: %s' % (T('类型', 'Type'), _route_label(result.get('route'))),
        '',
        result.get('final', ''),
    ]
    if result.get('work_order'):
        lines += ['', '## %s' % T('维修工单草稿', 'Work order draft'), '', result.get('work_order')]
    return '\n'.join(lines) + '\n'


def _history_push(result):
    """把本次结果收进“我的 · 历史问答”，同一问题只保留最新一条。"""
    query = (result.get('user_query') or '').strip()
    if not query:
        return
    entry = {
        'ts': time.strftime('%Y-%m-%d %H:%M'),
        'record_ts': time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_query': query,
        'route': result.get('route', 'normal'),
        'lang': LANG,
        'final': result.get('final') or '',
        'work_order': result.get('work_order') or '',
        'qa_id': (result.get('qa') or {}).get('编号', ''),
        'device': result.get('device') or '',
        'alarm': result.get('alarm_code') or '',
    }
    hist = list(st.session_state.get('history') or [])
    for i, old in enumerate(hist):
        if old.get('user_query') == query:
            hist[i] = entry
            break
    else:
        hist.append(entry)
    st.session_state.history = hist[-40:]


def _render_followups(result):
    sugs = result.get('suggestions') or []
    if not sugs:
        return
    st.markdown('<div class="zv-sug-title">%s</div>' % T('你可能还想问', 'You may also ask'), unsafe_allow_html=True)
    cols = st.columns(min(len(sugs), 4))
    for i, s in enumerate(sugs[:4]):
        with cols[i]:
            st.button(s, key='sug_%s_%d' % (result.get('_run_id', '0'), i), on_click=_ask, args=(s,),
                      use_container_width=True)


def _render_trace(result):
    if not st.session_state.get('trace_on', True):
        return
    trace = result.get('trace') or []
    if not trace:
        return
    with st.expander(T('多智能体执行轨迹 · 可观测性', 'Multi-agent execution trace'), expanded=True):
        st.markdown(_timeline_html(trace), unsafe_allow_html=True)


def _render_qa(result):
    qa = result.get('qa')
    if qa:
        case = result.get('qa_case') or {}
        case_title = (case.get('标题EN') if LANG == 'en' else _case_title(case)) or ''
        st.markdown(_banner(
            'ok',
            T('知识问答 · 命中知识库条目', 'Knowledge Q&A · answered from the knowledge base'),
            T('回答来自已收录的问答条目 %s，引用可追溯；现场操作须由持证人员确认。',
              'Answered from recorded FAQ entry %s with a traceable citation; on-site work requires certified personnel.')
            % qa.get('编号', '')), unsafe_allow_html=True)
        st.markdown(_tiles([
            (T('问题来源', 'FAQ entry'), qa.get('编号', '')),
            (T('关联案例', 'Related case'), '%s %s' % (qa.get('案例编号', ''), case_title)),
            (T('相关度', 'Relevance'), '%.0f%%' % (float(qa.get('得分', 0)) * 100)),
            (T('依据', 'Source'), qa.get('依据', '')),
        ]), unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="zv-qa"><div class="zv-qa-label">%s</div>'
                        '<div class="zv-qa-text">%s</div></div>'
                        % (T('回答', 'ANSWER'), _esc(qa.get('答案', ''))), unsafe_allow_html=True)
        note = result.get('audit_note') or ''
        if note:
            st.markdown('<div class="zv-audit">%s</div>' % _esc(note), unsafe_allow_html=True)
    else:
        st.markdown(_banner(
            'info',
            T('未收录该问题 · 不作猜测', 'Not covered · no speculative answer'),
            T('知识库中没有与该问题匹配的条目，系统不会用关键词拼接答案；可在下方已收录问题中重新选择。',
              'No matching FAQ entry was found, so no keyword-assembled answer is produced. Pick one of the answerable questions below.')),
            unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        '<div class="zv-note">%s</div>'
                        % (T('处理说明', 'Handling note'), T('审核兜底智能体', 'Audit & Safety Agent'),
                           T('系统如实说明证据不足，不作推测；如属设备故障，请补充设备编号与报警代码后重新提交。',
                             'The system states the evidence gap honestly and does not guess. For an equipment fault, '
                             'add the device ID and alarm code and submit again.')), unsafe_allow_html=True)


def _render_result(result):
    route = result.get('route', 'normal')
    hits = result.get('retrieved') or []
    device = result.get('device') or T('未识别', 'Unknown')
    alarm = result.get('alarm_code') or '—'

    if route == 'qa':
        _render_qa(result)
        _render_followups(result)
        _render_trace(result)
        return

    if route == 'high_risk':
        st.markdown(_banner('danger', T('高危工况 · 已强制转人工', 'High-risk condition · escalated to human'),
                            T('系统只输出停机与上报建议，不提供自动处置步骤，也不生成工单草稿。',
                              'Only shutdown and reporting guidance is provided. No automatic actions or work order drafts.')),
                    unsafe_allow_html=True)
    elif route == 'reject':
        st.markdown(_banner('warn', T('越界请求 · 已按只读边界拦截', 'Out-of-scope request · blocked'),
                            T('系统不接入设备控制，不修改 PLC 参数与工艺配置，请按管理制度由授权人员执行。',
                              'The system does not connect to the control system and never changes PLC parameters. '
                              'Authorized personnel must act under the management procedure.')),
                    unsafe_allow_html=True)
    elif not hits:
        st.markdown(_banner('info', T('未命中知识库 · 已拒绝作答', 'No knowledge base match · no speculative answer'),
                            T('系统如实声明证据不足，不作猜测；建议核对设备型号与报警代码后重试，或转人工咨询。',
                              'The system states the evidence gap honestly. Verify the device model and alarm code, '
                              'or escalate to a human.')),
                    unsafe_allow_html=True)
    else:
        st.markdown(_banner('ok', T('诊断完成 · 结论附条款级引用', 'Diagnosis complete · clause-level citations'),
                            T('设备 %s · 报警 %s · 命中 %d 个案例，所有建议须由持证维修人员现场确认后执行。',
                              'Device %s · Alarm %s · %d case(s) matched. All recommendations require on-site '
                              'confirmation by certified maintenance personnel.')
                            % (device, alarm, len(hits))), unsafe_allow_html=True)

    if route == 'normal' and hits:
        first = hits[0]
        match_map = {'报警号精确匹配': 'Alarm code exact match', '关键词+向量': 'Keyword + vector', '关键词': 'Keyword'}
        first_title = first.get('标题EN') if LANG == 'en' else _case_title(first)
        match_mode = first.get('命中方式', '')
        if LANG == 'en':
            match_mode = match_map.get(match_mode, match_mode)
        st.markdown(_tiles([
            (T('设备', 'Device'), device),
            (T('报警代码', 'Alarm code'), alarm),
            (T('命中案例', 'Matched case'), '%s %s' % (first.get('案例编号', ''), first_title)),
            (T('命中方式', 'Match mode'), match_mode or 'TBD'),
        ]), unsafe_allow_html=True)

        left, right = st.columns([1.55, 1], gap='medium')
        with left:
            with st.container(border=True):
                st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                            % (T('可能原因', 'Possible causes'), T('按概率排序', 'Ranked by probability')),
                            unsafe_allow_html=True)
                st.markdown(_causes_html(result.get('causes') or [], result.get('refs') or []),
                            unsafe_allow_html=True)
            checks = result.get('checks') or []
            if checks:
                with st.container(border=True):
                    st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                                % (T('现场确认项', 'On-site verification'),
                                   T('可逐项勾选，全部核对后再动手', 'Tick each item before maintenance')),
                                unsafe_allow_html=True)
                    done = 0
                    for i, c in enumerate(checks):
                        if st.checkbox(c, key='chk_%s_%d' % (result.get('_run_id', '0'), i)):
                            done += 1
                    progress_text = ('Verified %d/%d' if LANG == 'en' else '已核对 %d/%d 项') % (done, len(checks))
                    st.progress(done / float(len(checks)), text=progress_text)
                    if done == len(checks):
                        st.markdown('<div class="zv-confirm">%s</div>'
                                    % T('全部确认项已核对，可推进工单审批与派工。',
                                        'All items verified. The work order can now move to approval and dispatch.'),
                                    unsafe_allow_html=True)
        with right:
            with st.container(border=True):
                st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                            % (T('关联备件库存', 'Related spare parts'), T('模拟数据', 'Simulated data')),
                            unsafe_allow_html=True)
                st.markdown(_stock_list(result.get('stock') or []), unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                            % (T('引用来源', 'Sources'), T('条款级可追溯', 'Clause-level traceability')),
                            unsafe_allow_html=True)
                st.markdown(_sources_html(hits), unsafe_allow_html=True)

        work_order = result.get('work_order') or ''
        if work_order:
            with st.container(border=True):
                st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                            % (T('维修工单草稿', 'Maintenance work order draft'),
                               T('字段完整，待人工确认后派工', 'Complete fields, dispatch after human confirmation')),
                            unsafe_allow_html=True)
                st.code(work_order, language=None)

        note = result.get('audit_note') or ''
        if note:
            st.markdown('<div class="zv-audit">%s</div>' % _esc(note), unsafe_allow_html=True)
    else:
        note = result.get('audit_note') or ''
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        % (T('处理说明', 'Handling note'), T('审核兜底智能体', 'Audit & Safety Agent')),
                        unsafe_allow_html=True)
            st.markdown('<div class="zv-note">%s</div>' % _esc(note), unsafe_allow_html=True)

    _render_followups(result)
    _render_trace(result)


def _file_stamp(ts):
    return re.sub(r'[^0-9]', '', ts or '') or time.strftime('%Y%m%d_%H%M')


def _clear_history():
    st.session_state.history = []


def _on_dismiss_my():
    st.session_state.show_my = False


def _clear_todos():
    st.session_state.todos = []


def _add_todo():
    text = (st.session_state.get('todo_new') or '').strip()
    if not text:
        return
    todos = list(st.session_state.get('todos') or [])
    todos.append({'id': time.time_ns(), 'text': text, 'done': False})
    st.session_state.todos = todos


def _todo_from_record(e):
    label = ' '.join(x for x in [(e.get('alarm') or '').strip(), (e.get('device') or '').strip()]
                     if x and x not in ('未识别', 'Unknown'))
    if not label:
        label = _rec_preview(e.get('user_query'), 26)
    text = (T('跟进：%s', 'Follow up: %s') % label).strip()
    todos = list(st.session_state.get('todos') or [])
    if any(t.get('text') == text for t in todos):
        return
    todos.append({'id': time.time_ns(), 'text': text, 'done': False})
    st.session_state.todos = todos


def _del_todo(tid):
    st.session_state.todos = [t for t in (st.session_state.get('todos') or []) if t.get('id') != tid]


def _on_trace_change():
    st.session_state.trace_on = bool(st.session_state.get('trace_toggle', True))
    st.rerun(scope='app')


def _rec_preview(text, limit=110):
    s = re.sub(r'\s+', ' ', (text or '').strip())
    return s[:limit] + ('…' if len(s) > limit else '')


def _scope_label(value):
    return {
        'all': T('全部', 'All'),
        'normal': T('诊断', 'Diagnosis'),
        'qa': T('问答', 'Q&A'),
        'blocked': T('拦截', 'Blocked'),
    }.get(value, value)


@st.dialog(T('我的 · 工作台', 'My workspace'), width='large', on_dismiss=_on_dismiss_my)
def _my_dialog():
    hist = list(st.session_state.get('history') or [])
    reports = [e for e in hist if e.get('work_order')]
    todos = list(st.session_state.get('todos') or [])
    open_todos = len([t for t in todos if not t.get('done')])

    st.markdown(
        '<div class="zv-my-head"><div class="zv-my-eyebrow">MY WORKSPACE · 个人工作台</div>'
        '<div class="zv-my-title">%s</div><div class="zv-my-sub">%s</div>'
        '<div class="zv-my-chips">%s</div></div>'
        % (T('我的', 'My workspace'),
           T('以往的问答、报告单、待办与界面设置都收在这里，仅保存在当前浏览器会话。',
             'Past Q&A, reports, to-dos and settings live here, kept in this browser session.'),
           ''.join('<span class="zv-my-chip">%s</span>' % _esc(x) for x in [
               T('历史 %d 条', 'History %d') % len(hist),
               T('报告单 %d 份', 'Reports %d') % len(reports),
               T('待办 %d 项', 'To-dos %d') % open_todos,
               T('界面 %s', 'Language %s') % T('中文', 'English'),
           ])),
        unsafe_allow_html=True)

    view = st.segmented_control(
        T('分区', 'Section'),
        ['hist', 'report', 'todo', 'set'],
        format_func=lambda v: {
            'hist': T('历史问答', 'History'),
            'report': T('报告单', 'Reports'),
            'todo': T('待办清单', 'To-dos'),
            'set': T('设置', 'Settings'),
        }[v],
        key='my_view', label_visibility='collapsed',
    ) or 'hist'
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    # ---------- 历史问答 ----------
    if view == 'hist':
        if not hist:
            st.markdown('<div class="zv-empty"><b>%s</b>%s</div>'
                        % (T('还没有记录', 'No records yet'),
                           T('在上方提问或点一个快捷用例，结果会自动收进这里。',
                             'Ask a question above and results will be collected here.')),
                        unsafe_allow_html=True)
        else:
            fc1, fc2 = st.columns([1.8, 1])
            with fc1:
                kw = st.text_input(T('搜索记录', 'Search'), key='my_kw',
                                   placeholder=T('输入问题、设备编号或报警号', 'Question, device or alarm'),
                                   label_visibility='collapsed')
            with fc2:
                scope = st.selectbox(T('类型', 'Type'), ['all', 'normal', 'qa', 'blocked'],
                                     format_func=_scope_label, key='my_scope',
                                     label_visibility='collapsed')
            allowed = {'all': None, 'normal': ('normal',), 'qa': ('qa',),
                       'blocked': ('high_risk', 'reject')}.get(scope)
            q = (kw or '').strip().lower()
            shown = []
            for e in reversed(hist):
                if allowed and e.get('route') not in allowed:
                    continue
                blob = ' '.join(str(e.get(k) or '') for k in
                                ('user_query', 'device', 'alarm', 'qa_id')).lower()
                if q and q not in blob:
                    continue
                shown.append(e)
            if not shown:
                st.markdown('<div class="zv-empty"><b>%s</b>%s</div>'
                            % (T('没有匹配的记录', 'No matching records'),
                               T('换个关键词，或把类型切回“全部”。',
                                 'Try another keyword, or switch the type back to “All”.')),
                            unsafe_allow_html=True)
            for i, e in enumerate(shown[:14]):
                with st.container(border=True):
                    meta = ' · '.join(x for x in [e.get('device'), e.get('alarm'), e.get('qa_id')] if x)
                    st.markdown(
                        '<div class="zv-rec-head"><span class="zv-tag">%s</span>'
                        '<span class="zv-rec-time">%s</span></div>'
                        '<div class="zv-rec-title">%s</div><div class="zv-rec-meta">%s</div>'
                        '<div class="zv-rec-prev">%s</div>'
                        % (_esc(_route_label(e.get('route'))), _esc(e.get('ts', '')),
                           _esc(e.get('user_query', '')), _esc(meta),
                           _esc(_rec_preview(e.get('final')))),
                        unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([1.9, 1, 1])
                    with c1:
                        with st.expander(T('查看完整结论', 'View full result')):
                            st.markdown('<div class="zv-note">%s</div>' % _esc(e.get('final', '')),
                                        unsafe_allow_html=True)
                            if e.get('work_order'):
                                st.code(e.get('work_order'), language=None)
                    with c2:
                        st.download_button(T('导出', 'Export'), data=_export_text(e),
                                           file_name='zhizhi_record_%s.md' % _file_stamp(e.get('record_ts', '')),
                                           mime='text/markdown', key='hist_dl_%d' % i,
                                           use_container_width=True)
                    with c3:
                        st.button(T('加入待办', 'Add to-do'), key='hist_todo_%d' % i,
                                  on_click=_todo_from_record, args=(e,), use_container_width=True)

    # ---------- 报告单 ----------
    if view == 'report':
        if not reports:
            st.markdown('<div class="zv-empty"><b>%s</b>%s</div>'
                        % (T('暂无报告单', 'No reports yet'),
                           T('完成一次故障诊断后，维修工单草稿会自动归档到这里。',
                             'Work order drafts are archived here after a diagnosis.')),
                        unsafe_allow_html=True)
        else:
            rcols = st.columns(2, gap='medium')
            for i, e in enumerate(reports[:8]):
                with rcols[i % 2]:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="zv-rec-head"><span class="zv-tag">%s</span>'
                            '<span class="zv-rec-time">%s</span></div>'
                            '<div class="zv-rec-title">%s</div><div class="zv-rec-meta">%s</div>'
                            % (T('工单草稿', 'Work order'), _esc(e.get('ts', '')),
                               _esc(e.get('alarm') or e.get('device') or T('未标注', '—')),
                               _esc(_rec_preview(e.get('user_query'), 42))),
                            unsafe_allow_html=True)
                        with st.expander(T('查看报告单', 'View report')):
                            st.code(e.get('work_order', ''), language=None)
                        st.download_button(T('下载 Markdown', 'Download Markdown'), data=_export_text(e),
                                           file_name='work_order_%s.md' % _file_stamp(e.get('record_ts', '')),
                                           mime='text/markdown', key='rep_dl_%d' % i,
                                           use_container_width=True)

    # ---------- 待办清单 ----------
    if view == 'todo':
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        % (T('新增待办', 'New to-do'),
                           T('人工跟进事项，例如更换备件、复盘报警', 'Manual follow-ups such as part replacement')),
                        unsafe_allow_html=True)
            with st.form('todo_form', clear_on_submit=True, border=False):
                ti, tb = st.columns([3.2, 1])
                with ti:
                    st.text_input(T('待办内容', 'To-do'), key='todo_new', label_visibility='collapsed',
                                  placeholder=T('记下需要人工跟进的事项…', 'Note something to follow up…'))
                with tb:
                    if st.form_submit_button(T('添加', 'Add'), use_container_width=True):
                        _add_todo()
        if not todos:
            st.markdown('<div class="zv-empty"><b>%s</b>%s</div>'
                        % (T('暂无待办', 'No to-dos'),
                           T('把需要现场跟进的事记在这里，勾选即可标记完成。',
                             'Note on-site follow-ups here and tick them off when done.')),
                        unsafe_allow_html=True)
        else:
            done_cnt = 0
            for t in todos:
                c1, c2 = st.columns([4.6, 1])
                with c1:
                    checked = st.checkbox(t.get('text', ''), value=bool(t.get('done')),
                                          key='todo_chk_%s' % t.get('id'))
                    if checked != bool(t.get('done')):
                        t['done'] = checked
                        st.session_state.todos = todos
                with c2:
                    st.button(T('删除', 'Delete'), key='todo_del_%s' % t.get('id'),
                              on_click=_del_todo, args=(t.get('id'),), use_container_width=True)
                if checked:
                    done_cnt += 1
            st.progress(done_cnt / float(len(todos)), text='%d/%d' % (done_cnt, len(todos)))
            if done_cnt == len(todos):
                st.markdown('<div class="zv-confirm">%s</div>'
                            % T('待办已全部完成。', 'All to-dos completed.'), unsafe_allow_html=True)

    # ---------- 设置 ----------
    if view == 'set':
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        % (T('界面语言', 'Interface language'),
                           T('切换后用当前问题自动重跑', 'Re-runs the current question')),
                        unsafe_allow_html=True)
            st.segmented_control('lang', ['中文', 'English'], key='lang_choice',
                                 label_visibility='collapsed', on_change=_on_lang_change)
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        % (T('展示偏好', 'Display'), T('作用于主页面', 'Applies to the main page')),
                        unsafe_allow_html=True)
            st.toggle(T('显示多智能体执行轨迹', 'Show multi-agent execution trace'),
                      key='trace_toggle', value=st.session_state.get('trace_on', True),
                      on_change=_on_trace_change)
        with st.container(border=True):
            st.markdown('<div class="zv-card-title">%s<span class="zv-card-sub">%s</span></div>'
                        % (T('数据管理', 'Data'), T('仅保存在当前会话', 'This session only')),
                        unsafe_allow_html=True)
            st.markdown('<div class="zv-tool-note">%s</div>'
                        % (T('知识库 %d 个案例 / %d 条问答；历史 %d 条、报告 %d 份、待办 %d 项。',
                             '%d cases / %d FAQ entries · history %d · reports %d · to-dos %d')
                           % (len(RETRIEVER.cases), len(getattr(RETRIEVER, 'faqs', []) or []),
                              len(hist), len(reports), len(todos))),
                        unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                st.button(T('清空历史记录', 'Clear history'), key='clear_hist',
                          on_click=_clear_history, use_container_width=True)
            with b2:
                st.button(T('清空待办', 'Clear to-dos'), key='clear_todos',
                          on_click=_clear_todos, use_container_width=True)


# ---------------- 页面主体 ----------------
with st.container(key='myfab'):
    _hist_n = len(st.session_state.get('history') or [])
    if st.button(T('我的', 'My') + (' · %d' % _hist_n if _hist_n else ''),
                 key='btn_my', use_container_width=False):
        st.session_state.show_my = True

st.markdown("""
<div class="zv-hero">
  <div class="zv-hero-inner">
    <div class="zv-eyebrow">SMARTMAINT · 智能运维原型 / INTELLIGENT MAINTENANCE PROTOTYPE</div>
    <div class="zv-title">%s</div>
    <div class="zv-desc">%s</div>
    <div class="zv-badges">
      <span>LangGraph %s</span>
      <span>%s</span>
      <span>%s</span>
      <span>%s</span>
    </div>
  </div>
</div>
""" % (
    T('智维 · 车间设备故障诊断与维修协同智能体',
      'SmartMaint · Multi-Agent Equipment Fault Diagnosis & Maintenance Assistant'),
    T('面向车间一线维修场景：输入报警描述或维护问题，输出诊断结论、现场确认项、备件库存与维修工单草稿。'
      '六个智能体协同编排，结论附条款级引用；知识库未收录时如实说明，绝不编造。',
      'Built for shop-floor maintenance: enter an alarm description or a maintenance question to get a diagnosis, '
      'on-site checklist, spare parts and a work order draft. Six coordinated agents cite clause-level sources and '
      'state evidence gaps honestly instead of fabricating answers.'),
    T('多智能体编排', 'multi-agent orchestration'),
    T('关键词 + 向量混合检索', 'keyword + vector hybrid retrieval'),
    T('只读安全边界', 'read-only safety boundary'),
    T('中英双语', 'bilingual ZH/EN'),
), unsafe_allow_html=True)

MODE_TEXT = T('大模型模式', 'LLM mode') if LLM_ON else T('离线规则模式', 'Offline rule mode')
MODE_NOTE = T('已配置 LLM_API_KEY', 'LLM_API_KEY configured') if LLM_ON else T('零 API Key 可演示', 'Works without an API key')
st.markdown('<div class="zv-stats">' + ''.join(
    '<div class="zv-stat"><div class="v">%s</div><div class="l">%s</div><div class="n">%s</div></div>'
    % (_esc(v), _esc(l), _esc(n)) for v, l, n in [
        (str(len(RETRIEVER.cases)), T('知识库案例', 'Knowledge cases'), T('条款级引用', 'Clause-level citations')),
        (str(ALARM_CNT), T('覆盖报警代码', 'Alarm codes'), T('精确匹配优先', 'Exact match first')),
        (str(len(STOCK)), T('备件库存条目', 'Spare part records'), T('模拟数据', 'Simulated data')),
        (MODE_TEXT, T('当前运行模式', 'Runtime mode'), MODE_NOTE),
    ]) + '</div>', unsafe_allow_html=True)

st.markdown(_sec('01', T('报警输入', 'Alarm input'),
                 T('支持报警截图 OCR 后粘贴的文本，自动识别设备编号与 ALM 报警号；也可直接提出维护问题',
                   'Paste OCR text from an alarm screenshot; device ID and ALM code are detected automatically. '
                   'Maintenance questions are also accepted.')), unsafe_allow_html=True)

if 'demo_query' not in st.session_state:
    st.session_state.demo_query = EXAMPLES[0][2] if LANG == 'zh' else EXAMPLES[0][3]

with st.container(border=True):
    query = st.text_area(
        T('报警现象描述', 'Alarm description'),
        key='demo_query',
        height=104,
        label_visibility='collapsed',
        placeholder=T('例如：M-003 主轴电机温度过高，报警 ALM-2041，请帮我看看怎么处理。',
                      'e.g. M-003 spindle motor is overheating, alarm ALM-2041. How should I handle it?'),
    )
    b1, b2 = st.columns([1.1, 3])
    with b1:
        run = st.button(T('启动多智能体处理', 'Run multi-agent analysis'), type='primary', use_container_width=True)
    with b2:
        st.caption(T('系统为只读诊断辅助，不接入设备控制系统，不会修改任何参数。',
                     'Read-only diagnostic assistance. No connection to the control system and no parameter changes.'))

    st.markdown('<div class="zv-chip-label">%s</div>' % T('快捷演示用例', 'Quick demo cases'), unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLES))
    for idx, item in enumerate(EXAMPLES):
        with cols[idx]:
            st.button(item[0] if LANG == 'zh' else item[1], key='ex_%d' % idx,
                      on_click=_pick, args=(item[2] if LANG == 'zh' else item[3],), use_container_width=True)

auto = st.session_state.pop('auto_run', False)
if (run and query.strip()) or auto:
    st.markdown(_sec('02', T('诊断与问答结果', 'Diagnosis & Q&A result'),
                     T('多智能体协作产物，按路由输出', 'Multi-agent output by route')), unsafe_allow_html=True)
    with st.spinner(T('多智能体协作中：分诊 → 问答/检索 → 诊断 → 备件工单 → 审核 → 回复',
                      'Agents working: triage → Q&A/retrieval → diagnosis → parts & order → audit → reply')):
        result = build_graph().invoke({'user_query': query.strip(), 'lang': LANG})
    result['_run_id'] = str(time.time_ns())[-9:]
    st.session_state.last_result = result
    st.session_state.last_query = query.strip()
    _history_push(result)
elif run:
    st.toast(T('请先输入报警现象描述', 'Please enter a description first'))

result = st.session_state.get('last_result')
if result:
    _render_result(result)

# ---------------- 底部：功能与设置 ----------------
st.markdown(_sec('03', T('功能与设置', 'Tools & settings'),
                 T('结果导出与会话重置；语言切换已收进“我的”',
                   'Export and reset; language switching now lives in “My”')), unsafe_allow_html=True)
with st.container(border=True):
    c1, c2 = st.columns(2, gap='medium')
    with c1:
        st.markdown('<div class="zv-tool-label">%s</div>' % T('导出结果 / EXPORT', 'EXPORT / 导出结果'),
                    unsafe_allow_html=True)
        st.download_button(
            T('导出诊断记录（Markdown）', 'Export record (Markdown)'),
            data=_export_text(result) if result else '',
            file_name='zhizhi_record_%s.md' % time.strftime('%Y%m%d_%H%M'),
            mime='text/markdown',
            disabled=not result,
            use_container_width=True,
        )
    with c2:
        st.markdown('<div class="zv-tool-label">%s</div>' % T('会话 / SESSION', 'SESSION / 会话'),
                    unsafe_allow_html=True)
        st.button(T('清空并重置', 'Reset session'), on_click=_reset, use_container_width=True)
    st.markdown('<div class="zv-tool-note">%s</div>'
                % T('语言切换、历史问答与报告单请点右上角“我的”；导出内容对应当前结果。',
                    'Language switching, Q&A history and reports are in “My” at the top right. '
                    'The export always reflects the current result.'), unsafe_allow_html=True)

# ---------------- 底部：学术论文 ----------------
st.markdown(_sec('04', T('研究与参考', 'Research & references'),
                 T('与预测性维护、检索增强生成、多智能体相关的公开论文',
                   'Public papers on predictive maintenance, RAG and multi-agent systems')), unsafe_allow_html=True)
papers_html = '<div class="zv-papers">' + ''.join(
    '<a class="zv-paper" href="%s" target="_blank" rel="noopener">'
    '<div class="zv-paper-top"><span class="zv-paper-venue">%s</span><span class="zv-paper-id">%s</span></div>'
    '<div class="zv-paper-title">%s</div><div class="zv-paper-authors">%s</div>'
    '<div class="zv-paper-why">%s</div></a>'
    % (p['url'], _esc(p['venue']), _esc(p['id']), _esc(p['title']), _esc(p['authors']),
       _esc(p['why_en'] if LANG == 'en' else p['why_zh']))
    for p in PAPERS) + '</div>'
st.markdown(papers_html, unsafe_allow_html=True)
st.markdown('<div class="zv-tool-note">%s</div>'
            % T('以上为公开出版物，仅作方法参考；项目知识库、备件与工单均为模拟数据。',
                'These are public publications cited for methodological reference. The knowledge base, spare parts '
                'and work orders in this demo are simulated.'), unsafe_allow_html=True)

st.markdown('<div class="zv-foot">%s</div>'
            % T('本原型仅用于教学演示，全部为模拟数据；系统为只读诊断辅助，不接入设备控制系统，'
                '所有处置须由持证维修人员现场确认后执行。',
                'This prototype is for educational demonstration with simulated data. It is a read-only diagnostic '
                'assistant that never connects to the control system; all actions require on-site confirmation by '
                'certified maintenance personnel.'), unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="zv-side-head">%s</div>' % T('演示资源', 'Demo resources'), unsafe_allow_html=True)
    st.markdown('<div class="zv-side-sub">%s</div>'
                % T('知识库案例 · 模拟数据已脱敏', 'Knowledge cases · simulated and anonymized'),
                unsafe_allow_html=True)
    for c in RETRIEVER.cases:
        risk = ('<span class="zv-tag danger">%s</span>' % T('高危', 'HIGH')) if c.get('高危') else ''
        code = ('<span class="zv-tag">%s</span>' % _esc(c['报警代码'])) if _has_code(c) \
            else '<span class="zv-tag muted">%s</span>' % T('无代码', 'No code')
        title = c.get('标题EN') if LANG == 'en' else _case_title(c)
        device = c.get('设备EN') if LANG == 'en' else c.get('设备')
        st.markdown('<div class="zv-case"><div class="zv-case-top"><span class="zv-code">%s</span>%s%s</div>'
                    '<div class="zv-case-title">%s</div><div class="zv-case-dev">%s</div></div>'
                    % (_esc(c.get('案例编号')), code, risk, _esc(title), _esc(device)),
                    unsafe_allow_html=True)

    st.markdown('<div class="zv-side-head sm">%s</div>' % T('备件库存', 'Spare parts'), unsafe_allow_html=True)
    st.markdown(_stock_list(STOCK), unsafe_allow_html=True)

    st.markdown('<div class="zv-side-head sm">%s</div>' % T('运行说明', 'Runtime'), unsafe_allow_html=True)
    st.markdown('<div class="zv-mode"><span class="zv-dot-mode %s"></span><div>'
                '<div class="zv-mode-t">%s</div><div class="zv-mode-d">%s</div></div></div>'
                % ('' if LLM_ON else 'off', _esc(MODE_TEXT),
                   T('已接入 DeepSeek，失败自动回退规则模式', 'DeepSeek connected; falls back to rule mode on failure')
                   if LLM_ON else
                   T('规则 + 混合检索完成全部推理；在 .env 填入 LLM_API_KEY 后自动切换',
                     'Rules and hybrid retrieval handle all reasoning; set LLM_API_KEY in .env to enable the LLM')),
                unsafe_allow_html=True)

if st.session_state.get('show_my'):
    _my_dialog()
