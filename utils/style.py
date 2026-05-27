import streamlit as st

PRIMARY   = "#1B2A4A"
PRIMARY_D = "#0F1B33"


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

    /* ── Global (body만 타겟, * 사용 안 함) ───────── */
    html, body, .stApp {
        font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
        background-color: #EEF2F7 !important;
    }
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px;
    }

    /* ── Sidebar: 배경 ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(170deg, #0A1628 0%, #1B2A4A 55%, #243656 100%) !important;
        border-right: none !important;
    }
    /* 사이드바 전체 텍스트 (네비게이션 포함) */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div[data-testid="stSidebarNavItems"] span,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] p,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .element-container p {
        color: #C8D8F0 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #A8BBDA !important;
    }
    /* 네비게이션 링크 hover */
    section[data-testid="stSidebar"] a:hover {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }
    /* 사이드바 selectbox 박스 */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div:first-child {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
    }
    /* selectbox 선택된 텍스트 */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] span {
        color: #E8F0FC !important;
    }

    /* ── 메인 영역 제목 ─────────────────────────────── */
    .main h1 {
        color: #0F1B33 !important;
        font-weight: 700 !important;
    }
    .main h2, .main h3 {
        color: #1B2A4A !important;
        font-weight: 600 !important;
    }

    /* ── Metric 카드 ─────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: white !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 2px 12px rgba(15,27,51,0.09) !important;
        border-left: 5px solid #1B2A4A !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #1B2A4A !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #64748B !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }

    /* ── 버튼 ────────────────────────────────────────── */
    .stButton > button {
        border-radius: 9px !important;
        font-weight: 500 !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1B2A4A 0%, #243656 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 3px 10px rgba(27,42,74,0.28) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #243656 0%, #2D4A70 100%) !important;
        box-shadow: 0 5px 16px rgba(27,42,74,0.38) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind]) {
        background: white !important;
        border: 1.5px solid #CBD5E1 !important;
        color: #475569 !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind]):hover {
        border-color: #1B2A4A !important;
        color: #1B2A4A !important;
        background: #F0F4F8 !important;
    }

    /* ── Container (border=True) ──────────────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.06) !important;
    }
    /* 컨테이너 내부 텍스트 색상 보장 */
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span {
        color: #1e293b;
    }

    /* ── Expander ────────────────────────────────────── */
    div[data-testid="stExpander"] {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        margin-bottom: 0.5rem !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] > details > summary {
        background: #F8FAFC !important;
        padding: 0.8rem 1rem !important;
        font-weight: 600 !important;
        color: #1B2A4A !important;
    }
    div[data-testid="stExpander"] > details > summary:hover {
        background: #F1F5F9 !important;
    }
    /* expander 내부 텍스트 보장 */
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] label {
        color: #1e293b !important;
    }

    /* ── Progress bar ────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1B2A4A, #3B5998) !important;
        border-radius: 4px !important;
    }
    .stProgress > div > div > div {
        background: #E2E8F0 !important;
        border-radius: 4px !important;
    }

    /* ── 입력 필드 ───────────────────────────────────── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: white !important;
        color: #1e293b !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #1B2A4A !important;
        box-shadow: 0 0 0 2px rgba(27,42,74,0.12) !important;
    }
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: white !important;
        color: #1e293b !important;
    }

    /* ── Form ────────────────────────────────────────── */
    div[data-testid="stForm"] {
        background: #F8FAFC !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── HR / Divider ────────────────────────────────── */
    hr { border-color: #E2E8F0 !important; }

    /* ── Alerts ──────────────────────────────────────── */
    div[data-testid="stAlert"] { border-radius: 10px !important; }

    /* ── Inline code ─────────────────────────────────── */
    code {
        background: #EFF6FF !important;
        color: #1B2A4A !important;
        border-radius: 5px !important;
        padding: 2px 7px !important;
    }

    /* ── Spinner ─────────────────────────────────────── */
    .stSpinner > div { border-top-color: #1B2A4A !important; }
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    sub_html = (f'<div style="opacity:0.75;font-size:0.88rem;margin-top:0.3rem">'
                f'{subtitle}</div>') if subtitle else ''
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0A1628 0%, #1B2A4A 65%, #2D4270 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(15,27,51,0.2);
    ">
        <div style="font-size:1.8rem;font-weight:700;letter-spacing:-0.3px;color:white">
            {icon}&nbsp; {title}
        </div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, icon: str = "", color: str = PRIMARY):
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 2px 12px rgba(15,27,51,0.08);
        border-left: 5px solid {color};
    ">
        <div style="font-size:0.72rem;color:#64748B;text-transform:uppercase;
                    letter-spacing:0.7px;margin-bottom:0.5rem;font-weight:500">
            {icon}&nbsp; {label}
        </div>
        <div style="font-size:2rem;font-weight:700;color:{color};line-height:1">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    colors = {
        'active':    ('#dcfce7', '#15803d', '진행 중'),
        'paused':    ('#fef9c3', '#854d0e', '일시정지'),
        'completed': ('#f1f5f9', '#475569', '완료'),
    }
    bg, fg, label = colors.get(status, ('#f1f5f9', '#475569', status))
    return (f'<span style="background:{bg};color:{fg};padding:3px 10px;'
            f'border-radius:20px;font-size:0.78rem;font-weight:600">{label}</span>')


def sidebar_brand():
    st.sidebar.markdown("""
    <div style="text-align:center;padding:1.2rem 0 1.6rem;
                border-bottom:1px solid rgba(255,255,255,0.12);margin-bottom:1.2rem">
        <div style="font-size:2.2rem;margin-bottom:0.4rem">📋</div>
        <div style="font-size:1rem;font-weight:700;color:white;letter-spacing:1.5px">
            업무일지 시스템
        </div>
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.45);margin-top:0.2rem">
            WorkLog Management
        </div>
    </div>
    """, unsafe_allow_html=True)
