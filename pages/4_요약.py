import streamlit as st
from datetime import date, timedelta
from utils.db import list_projects, list_members, list_logs
from utils.helpers import (
    start_of_week, end_of_week, start_of_month, end_of_month,
    latest_progress, week_label, month_label,
)
from utils.style import apply_styles, page_header

st.set_page_config(page_title="업무 요약", page_icon="📊", layout="wide")
apply_styles()
page_header("📊", "업무 요약")

# ── 범위 / 날짜 선택 ──────────────────────────────────────────
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
range_type = col1.radio("기간", ['weekly', 'monthly'], format_func=lambda x: '주간' if x == 'weekly' else '월간', horizontal=True)

if 'summary_anchor' not in st.session_state:
    st.session_state['summary_anchor'] = date.today().isoformat()

anchor = date.fromisoformat(st.session_state['summary_anchor'])

if col2.button("◀ 이전"):
    delta = timedelta(weeks=1) if range_type == 'weekly' else timedelta(days=32)
    st.session_state['summary_anchor'] = (anchor - delta).isoformat()
    st.rerun()

if col3.button("다음 ▶"):
    delta = timedelta(weeks=1) if range_type == 'weekly' else timedelta(days=28)
    st.session_state['summary_anchor'] = (anchor + delta).isoformat()
    st.rerun()

if range_type == 'weekly':
    start_date = start_of_week(anchor)
    end_date = end_of_week(anchor)
    label = week_label(anchor)
else:
    start_date = start_of_month(anchor)
    end_date = end_of_month(anchor)
    label = month_label(anchor)

col4.markdown(f"**{label}**  \n{start_date} ~ {end_date}")

st.divider()

# ── 데이터 로드 ───────────────────────────────────────────────
projects = list_projects()
members = list_members()
all_logs = list_logs()
member_map = {m['id']: m for m in members}

start_str = start_date.isoformat()
end_str = end_date.isoformat()
period_logs = [l for l in all_logs if start_str <= l['date'] <= end_str]

if not period_logs:
    st.info(f"해당 기간({start_str} ~ {end_str})에 등록된 업무일지가 없습니다.")
    st.stop()

# ── 프로젝트별 요약 ───────────────────────────────────────────
for p in projects:
    p_logs = [l for l in all_logs if l['project_id'] == p['id']]
    p_period = [l for l in period_logs if l['project_id'] == p['id']]
    if not p_period:
        continue

    prog = latest_progress(p_logs)
    total_hours = sum(l.get('hours') or 0 for l in p_period)
    all_items = list(dict.fromkeys(
        it.strip() for l in p_period for it in (l.get('items') or []) if it.strip()
    ))

    with st.container(border=True):
        hc1, hc2, hc3 = st.columns([4, 1, 1])
        hc1.markdown(f"### {p['name']}")
        hc2.metric("진척률", f"{prog}%")
        hc3.metric("총 공수", f"{total_hours}h")
        st.progress(prog / 100)

        # 팀원별 공수 & 항목
        mc1, mc2 = st.columns([1, 2])
        with mc1:
            st.markdown("**팀원별 공수**")
            member_hours: dict[str, float] = {}
            for l in p_period:
                mid = l['member_id']
                member_hours[mid] = member_hours.get(mid, 0) + (l.get('hours') or 0)
            for mid, h in sorted(member_hours.items(), key=lambda x: -x[1]):
                name = member_map.get(mid, {}).get('name', '?')
                st.markdown(f"- **{name}**: {h}h")

        with mc2:
            st.markdown("**수행 업무 항목**")
            for it in all_items:
                st.markdown(f"- {it}")

