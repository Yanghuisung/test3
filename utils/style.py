import streamlit as st

# ── Design System Tokens (Worklog Design System) ──────────────
NAVY_900 = "#0A1428"
NAVY_800 = "#0F1B33"
NAVY_700 = "#1B2A4A"
NAVY_600 = "#2A3A5C"
NAVY_500 = "#4A5A7C"
NAVY_400 = "#7A89AB"
NAVY_300 = "#B8C0D6"
NAVY_200 = "#DDE2EE"
NAVY_100 = "#F0F2F8"
NAVY_50  = "#F8F9FC"

ACCENT   = "#3D6FE0"

STATUS_ACTIVE    = "#00855A"
STATUS_ACTIVE_BG = "rgba(0,133,90,0.12)"
STATUS_PAUSED    = "#D4760A"
STATUS_PAUSED_BG = "rgba(212,118,10,0.12)"
STATUS_DONE      = NAVY_700
STATUS_DONE_BG   = "rgba(27,42,74,0.12)"
STATUS_WARN      = "#C8102E"
STATUS_WARN_BG   = "rgba(200,16,46,0.12)"

# Legacy alias kept for callers
PRIMARY   = NAVY_700
PRIMARY_D = NAVY_800

_WORKLOG_MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="8" fill="#0046C8"/>
  <path d="M9.5 7.5h5.8c2.8 0 5 .7 6.6 2.2 1.6 1.4 2.4 3.4 2.4 5.9 0 2.6-.8 4.7-2.5 6.2-1.6 1.5-3.9 2.2-6.7 2.2H9.5V7.5zm3.4 2.8v11h2.2c1.9 0 3.4-.5 4.4-1.5 1-.9 1.6-2.3 1.6-4 0-1.7-.5-3.1-1.5-4.1-1-1-2.5-1.5-4.4-1.5h-2.3z" fill="#fff"/>
</svg>"""


def apply_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* ── Global ─────────────────────────────────────────────── */
    html, body, .stApp {{
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: {NAVY_50} !important;
        color: {NAVY_800} !important;
        word-break: keep-all;
        -webkit-font-smoothing: antialiased;
    }}
    .main .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px;
    }}

    /* ── Sidebar ────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(170deg, {NAVY_900} 0%, {NAVY_700} 55%, {NAVY_600} 100%) !important;
        border-right: none !important;
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] span,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] p,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .element-container p {{
        color: #C8D8F0 !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #FFFFFF !important;
        border: none !important;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
        color: {NAVY_400} !important;
    }}
    section[data-testid="stSidebar"] a:hover {{
        color: #FFFFFF !important;
        text-decoration: none !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div:first-child {{
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] span {{
        color: #E8F0FC !important;
    }}

    /* ── Main headings ──────────────────────────────────────── */
    .main h1 {{
        color: {NAVY_800} !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }}
    .main h2, .main h3 {{
        color: {NAVY_800} !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em !important;
    }}

    /* ── Metric (KPI) 카드 ──────────────────────────────────── */
    div[data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 16px 18px !important;
        border: 1px solid {NAVY_200} !important;
        box-shadow: 0 1px 3px rgba(15,27,51,0.06) !important;
    }}
    div[data-testid="stMetricValue"] > div {{
        color: {NAVY_800} !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
    }}
    div[data-testid="stMetricLabel"] > div {{
        color: {NAVY_500} !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}

    /* ── 버튼 ───────────────────────────────────────────────── */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.05s ease !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {NAVY_700} !important;
        border: 1px solid {NAVY_700} !important;
        color: #fff !important;
        box-shadow: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: {NAVY_800} !important;
        border-color: {NAVY_800} !important;
    }}
    .stButton > button[kind="primary"]:active {{
        transform: translateY(1px) !important;
    }}
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind]) {{
        background: {NAVY_50} !important;
        border: 1px solid {NAVY_200} !important;
        color: {NAVY_800} !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind]):hover {{
        background: {NAVY_100} !important;
        border-color: {NAVY_300} !important;
    }}

    /* ── Container (border=True) ────────────────────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid {NAVY_200} !important;
        box-shadow: 0 1px 3px rgba(15,27,51,0.06) !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span {{
        color: {NAVY_800};
    }}

    /* ── Expander ───────────────────────────────────────────── */
    div[data-testid="stExpander"] {{
        background: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid {NAVY_200} !important;
        box-shadow: 0 1px 3px rgba(15,27,51,0.06) !important;
        margin-bottom: 0.5rem !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] > details > summary {{
        background: {NAVY_50} !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        color: {NAVY_800} !important;
    }}
    div[data-testid="stExpander"] > details > summary:hover {{
        background: {NAVY_100} !important;
    }}
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] label {{
        color: {NAVY_800} !important;
    }}

    /* ── Progress bar ───────────────────────────────────────── */
    .stProgress > div > div > div > div {{
        background: {NAVY_700} !important;
        border-radius: 4px !important;
        transition: width 0.3s ease !important;
    }}
    .stProgress > div > div > div {{
        background: {NAVY_200} !important;
        border-radius: 4px !important;
    }}

    /* ── 입력 필드 ──────────────────────────────────────────── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {{
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #fff !important;
        color: {NAVY_800} !important;
        font-size: 14px !important;
    }}
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {{
        border-color: {NAVY_700} !important;
        box-shadow: 0 0 0 2px rgba(27,42,74,0.12) !important;
    }}
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div {{
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #fff !important;
        color: {NAVY_800} !important;
    }}

    /* ── Form ───────────────────────────────────────────────── */
    div[data-testid="stForm"] {{
        background: {NAVY_50} !important;
        border-radius: 10px !important;
        border: 1px solid {NAVY_200} !important;
    }}

    /* ── HR / Divider ───────────────────────────────────────── */
    hr {{ border-color: {NAVY_200} !important; }}

    /* ── Alerts ─────────────────────────────────────────────── */
    div[data-testid="stAlert"] {{ border-radius: 8px !important; }}

    /* ── Inline code ────────────────────────────────────────── */
    code {{
        font-family: 'JetBrains Mono', monospace !important;
        background: {NAVY_100} !important;
        color: {NAVY_700} !important;
        border-radius: 5px !important;
        padding: 2px 7px !important;
        font-size: 0.92em !important;
    }}

    /* ── Spinner ────────────────────────────────────────────── */
    .stSpinner > div {{ border-top-color: {ACCENT} !important; }}

    /* ── Chat messages ──────────────────────────────────────── */
    div[data-testid="stChatMessage"] {{
        border-radius: 10px !important;
        border: 1px solid {NAVY_200} !important;
    }}

    /* ── Dataframe / table header ───────────────────────────── */
    div[data-testid="stDataFrame"] th {{
        background: {NAVY_50} !important;
        color: {NAVY_500} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    sub_html = (
        f'<div style="opacity:0.75;font-size:0.88rem;margin-top:0.35rem;'
        f'letter-spacing:0.01em">{subtitle}</div>'
    ) if subtitle else ''
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {NAVY_700} 0%, {NAVY_800} 50%, {NAVY_900} 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(15,27,51,0.18);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position:absolute;top:-30px;right:-20px;
            width:140px;height:140px;border-radius:50%;
            background:rgba(61,111,224,0.15);pointer-events:none
        "></div>
        <div style="
            position:absolute;bottom:-40px;right:80px;
            width:100px;height:100px;border-radius:50%;
            background:rgba(61,111,224,0.08);pointer-events:none
        "></div>
        <div style="position:relative">
            <div style="font-size:1.65rem;font-weight:800;letter-spacing:-0.02em;color:white;line-height:1.2">
                {icon}&nbsp; {title}
            </div>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, icon: str = "", color: str = NAVY_700,
                hint: str = ""):
    hint_html = (
        f'<div style="font-size:12px;color:{NAVY_400};margin-top:4px">{hint}</div>'
    ) if hint else ''
    st.markdown(f"""
    <div style="
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px 18px;
        border: 1px solid {NAVY_200};
        box-shadow: 0 1px 3px rgba(15,27,51,0.06);
        transition: box-shadow 0.2s ease;
    ">
        <div style="font-size:12px;color:{NAVY_500};text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:6px;font-weight:600">
            {icon}&nbsp; {label}
        </div>
        <div style="font-size:26px;font-weight:700;color:{color};line-height:1">{value}</div>
        {hint_html}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """프로젝트 상태 배지 HTML 반환"""
    mapping = {
        'active':    (STATUS_ACTIVE_BG,    STATUS_ACTIVE,    '진행 중'),
        'paused':    (STATUS_PAUSED_BG,    STATUS_PAUSED,    '보류'),
        'completed': (STATUS_DONE_BG,      STATUS_DONE,      '완료'),
        'warn':      (STATUS_WARN_BG,      STATUS_WARN,      '지연'),
        # 진척률 기반 alias
        'done':      (STATUS_DONE_BG,      STATUS_DONE,      '완료'),
        'delayed':   (STATUS_WARN_BG,      STATUS_WARN,      '지연'),
    }
    bg, fg, label = mapping.get(status, (NAVY_100, NAVY_500, status))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border-radius:999px;font-size:12px;font-weight:500">{label}</span>'
    )


def progress_badge(progress: int) -> str:
    """진척률 기반 상태 배지 HTML 반환"""
    if progress >= 100:
        return status_badge('completed')
    if progress > 0:
        return status_badge('active')
    return status_badge('paused')


def sidebar_brand():
    st.sidebar.markdown(f"""
    <div style="
        text-align:center;
        padding: 1.4rem 0 1.6rem;
        border-bottom: 1px solid rgba(255,255,255,0.10);
        margin-bottom: 1.2rem;
    ">
        <div style="display:flex;align-items:center;justify-content:center;gap:10px">
            {_WORKLOG_MARK_SVG}
            <div style="text-align:left">
                <div style="font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:-0.01em;line-height:1.1">
                    Work<span style="color:{ACCENT}">Log</span>
                </div>
                <div style="font-size:0.62rem;color:rgba(255,255,255,0.45);letter-spacing:0.08em;text-transform:uppercase;margin-top:1px">
                    한전KDN 전력ICT연구원
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
