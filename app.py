import streamlit as st
from datetime import date
from utils.db import list_projects, list_members, list_logs
from utils.helpers import start_of_week, end_of_week, latest_progress, today_str
from utils.style import apply_styles, page_header, metric_card, status_badge, sidebar_brand

st.set_page_config(
    page_title="업무일지 관리 시스템",
    page_icon="📋",
    layout="wide",
)
apply_styles()

# ── Sidebar ───────────────────────────────────────────────────
members = list_members()
member_map = {m['id']: m for m in members}

if 'current_user_id' not in st.session_state:
    st.session_state['current_user_id'] = ''

sidebar_brand()

with st.sidebar:
    st.markdown('<p style="font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;opacity:0.6;margin-bottom:0.2rem">현재 사용자</p>', unsafe_allow_html=True)
    user_ids = [''] + [m['id'] for m in members]

    def fmt_user(x):
        if not x: return '— 선택 안 함 —'
        m = member_map.get(x, {})
        return f"{m.get('name','')}  ({m.get('role','') or '-'})"

    st.selectbox("사용자 선택", options=user_ids, format_func=fmt_user,
                 key='current_user_id', label_visibility="collapsed")

    if st.session_state['current_user_id']:
        cu = member_map[st.session_state['current_user_id']]
        st.markdown(f"""
        <div style="margin-top:0.8rem;background:rgba(255,255,255,0.1);
                    border-radius:10px;padding:0.8rem 1rem">
            <div style="font-weight:600;color:white;font-size:1rem">{cu['name']}</div>
            <div style="font-size:0.78rem;opacity:0.65;margin-top:0.1rem">{cu.get('role') or '역할 미지정'}</div>
        </div>
        """, unsafe_allow_html=True)

# ── 대시보드 ──────────────────────────────────────────────────
page_header("📋", "업무일지 관리 시스템", today_str())

projects = list_projects()
logs = list_logs()
active = [p for p in projects if p['status'] == 'active']
today = date.today()
ws = start_of_week(today).isoformat()
we = end_of_week(today).isoformat()
week_logs = [l for l in logs if ws <= l['date'] <= we]

# ── 지표 카드 ─────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("전체 프로젝트", str(len(projects)), "🗂️", "#1B2A4A")
with c2: metric_card("진행 중", str(len(active)), "🟢", "#15803d")
with c3: metric_card("전체 팀원", str(len(members)), "👥", "#1d4ed8")
with c4: metric_card("이번 주 일지", str(len(week_logs)), "📝", "#b45309")

st.markdown("<br>", unsafe_allow_html=True)

# ── 진행 중 프로젝트 ──────────────────────────────────────────
st.markdown("### 🟢 진행 중 프로젝트")
if not active:
    st.info("진행 중인 프로젝트가 없습니다.")
else:
    cols = st.columns(min(len(active), 3))
    for i, p in enumerate(active):
        p_logs = [l for l in logs if l['project_id'] == p['id']]
        prog = latest_progress(p_logs)
        m_names = [member_map[mid]['name'] for mid in (p.get('member_ids') or []) if mid in member_map]
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"""
                <div style="border-bottom:1px solid #E2E8F0;padding-bottom:0.6rem;margin-bottom:0.6rem">
                    <div style="font-weight:700;font-size:1rem;color:#0F1B33">{p['name']}</div>
                    {f'<div style="font-size:0.8rem;color:#94A3B8;margin-top:2px">{p["description"]}</div>' if p.get('description') else ''}
                </div>
                """, unsafe_allow_html=True)
                if m_names:
                    st.caption(f"👤 {',  '.join(m_names)}")
                st.progress(prog / 100, text=f"진척률 {prog}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── 최근 업무일지 ─────────────────────────────────────────────
st.markdown("### 📝 최근 업무일지")
project_map = {p['id']: p['name'] for p in projects}
recent = sorted(logs, key=lambda l: (l['date'], l.get('created_at', '')), reverse=True)[:8]

if not recent:
    st.info("등록된 업무일지가 없습니다.")
else:
    for l in recent:
        proj_name = project_map.get(l['project_id'], '?')
        member = member_map.get(l['member_id'], {})
        items_str = " / ".join(l.get('items') or [])
        hours = l.get('hours')
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 1, 4])
            col1.markdown(f"**{l['date']}**")
            col2.markdown(f"`{proj_name}`")
            col3.markdown(
                f"**{member.get('name','?')}** — {items_str}"
                + (f"  ·  ⏱ {hours}h" if hours else "")
            )
