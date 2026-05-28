import streamlit as st
from datetime import date, timedelta
from utils.db import list_projects, list_members, list_logs, list_all_summaries
from utils.helpers import start_of_week, end_of_week, latest_progress, week_label
from utils.ai_utils import chat_response
from utils.style import apply_styles, page_header

st.set_page_config(page_title="AI 어시스턴트", page_icon="🤖", layout="wide")
apply_styles()
page_header("🤖", "AI 어시스턴트", "기간을 지정하면 해당 기간의 업무 보고서를 기반으로 질의응답합니다")

# ── 데이터 로드 ───────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_base_data():
    return list_projects(), list_members(), list_logs(), list_all_summaries()

projects, members, all_logs, all_summaries = load_base_data()
member_map  = {m['id']: m for m in members}
project_map = {p['id']: p for p in projects}
today       = date.today()


# ── 기간 내 주차 목록 반환 ────────────────────────────────────
def get_weeks(start: date, end: date) -> list[tuple[date, date]]:
    weeks, cur = [], start_of_week(start)
    while cur <= end:
        w_end = min(end_of_week(cur), end)
        w_start = max(cur, start)
        if w_start <= end:
            weeks.append((w_start, w_end))
        cur = end_of_week(cur) + timedelta(days=1)
    return weeks


# ── 기간 기반 컨텍스트 빌드 ───────────────────────────────────
def build_period_context(start: date, end: date) -> tuple[str, dict]:
    start_str = start.isoformat()
    end_str   = end.isoformat()

    period_logs = [l for l in all_logs if start_str <= l['date'] <= end_str]

    # ── 프로젝트별 기간 내 데이터 수집 ──────────────────────
    proj_sections = []
    for p in projects:
        p_logs     = [l for l in period_logs if l['project_id'] == p['id']]
        all_p_logs = [l for l in all_logs   if l['project_id'] == p['id']]
        if not p_logs:
            continue
        prog_start = latest_progress([l for l in all_p_logs if l['date'] < start_str])
        prog_end   = latest_progress(all_p_logs)
        mh: dict[str, float] = {}
        for l in p_logs:
            name = member_map.get(l['member_id'], {}).get('name', '?')
            mh[name] = mh.get(name, 0) + (l.get('hours') or 0)
        proj_sections.append({
            'name': p['name'], 'logs': p_logs,
            'prog_start': prog_start, 'prog_end': prog_end, 'mh': mh,
        })

    # ── 주차별 상세 내역 ──────────────────────────────────────
    weeks      = get_weeks(start, end)
    week_blocks = []
    sum_map    = {}   # (project_key, start, end) → content
    for s in all_summaries:
        if s['range'] == 'weekly':
            sum_map[(s['project_key'], s['start_date'], s['end_date'])] = s['content']

    for ws, we in weeks:
        ws_s, we_s = ws.isoformat(), we.isoformat()
        w_logs = [l for l in period_logs if ws_s <= l['date'] <= we_s]
        if not w_logs:
            continue

        lines = [f"▶ {week_label(ws)}  ({ws_s} ~ {we_s})"]
        for p in projects:
            pw_logs = [l for l in w_logs if l['project_id'] == p['id']]
            if not pw_logs:
                continue
            # AI 요약이 있으면 우선 사용
            ai_key = (p['id'], ws_s, we_s)
            if ai_key in sum_map:
                lines.append(f"  [{p['name']}] AI요약:\n    "
                             + sum_map[ai_key].replace('\n', '\n    ')[:600])
            else:
                items = list(dict.fromkeys(
                    it.strip() for l in pw_logs for it in (l.get('items') or []) if it.strip()
                ))
                members_str = ", ".join(dict.fromkeys(
                    member_map.get(l['member_id'], {}).get('name', '?') for l in pw_logs
                ))
                lines.append(f"  [{p['name']}] 담당: {members_str}")
                for it in items:
                    lines.append(f"    · {it}")
        week_blocks.append("\n".join(lines))

    # ── 팀원별 공수 합계 ──────────────────────────────────────
    total_mh: dict[str, float] = {}
    for l in period_logs:
        name = member_map.get(l['member_id'], {}).get('name', '?')
        total_mh[name] = total_mh.get(name, 0) + (l.get('hours') or 0)

    # ── 컨텍스트 문자열 조합 ──────────────────────────────────
    proj_status_lines = []
    for sec in proj_sections:
        delta = sec['prog_end'] - sec['prog_start']
        delta_str = f"+{delta}%" if delta >= 0 else f"{delta}%"
        mh_str = ", ".join(f"{n}({h}h)" for n, h in sorted(sec['mh'].items(), key=lambda x: -x[1]))
        proj_status_lines.append(
            f"  - {sec['name']}: {sec['prog_start']}% → {sec['prog_end']}% ({delta_str}) | "
            f"투입: {mh_str}"
        )

    member_total_lines = [
        f"  - {n}: {h}h"
        for n, h in sorted(total_mh.items(), key=lambda x: -x[1])
    ]

    context = f"""당신은 프로젝트 업무일지 AI 어시스턴트입니다.
아래는 지정된 기간의 실제 업무 보고서 데이터입니다. 이 데이터만을 근거로 답변하세요.

[답변 규칙]
- 한국어로 명확하고 간결하게 답변
- 데이터에 없는 내용은 "해당 기간 데이터에 없습니다"로 답변
- 수치(진척률·공수·날짜)는 반드시 데이터 기반 인용
- 표나 목록으로 정리하면 가독성이 높아지면 적극 사용
- 분석 기간: {start_str} ~ {end_str} ({len(weeks)}주)
- 오늘 날짜: {today.isoformat()}

[팀원 목록]
{chr(10).join(f"  - {m['name']} ({m.get('role') or '역할 미지정'})" for m in members)}

[기간별 프로젝트 진척 현황]
{chr(10).join(proj_status_lines) or "  (데이터 없음)"}

[팀원별 총 투입 공수]
{chr(10).join(member_total_lines) or "  (데이터 없음)"}

[주차별 상세 업무 내역]
{chr(10).join(week_blocks) or "  (데이터 없음)"}
"""

    meta = {
        'start': start_str,
        'end':   end_str,
        'weeks': len(weeks),
        'log_count': len(period_logs),
        'project_count': len(proj_sections),
        'projects': [s['name'] for s in proj_sections],
        'has_ai_summary': any(
            (p['id'], ws.isoformat(), we.isoformat()) in sum_map
            for ws, we in weeks for p in projects
        ),
    }
    return context, meta


# ── 세션 상태 초기화 ──────────────────────────────────────────
if 'chat_history'   not in st.session_state:
    st.session_state['chat_history']   = []
if 'period_context' not in st.session_state:
    st.session_state['period_context'] = None
if 'period_meta'    not in st.session_state:
    st.session_state['period_meta']    = None

# ── 레이아웃: 좌(설정) / 우(채팅) ────────────────────────────
left, right = st.columns([1, 2], gap="medium")

# ═══════════════════════════════════════════════════
# 좌측: 기간 설정 + 추천 질문
# ═══════════════════════════════════════════════════
with left:

    # ── 기간 선택 ─────────────────────────────────────────────
    with st.container(border=True):
        st.markdown("**📅 보고서 기간 설정**")

        default_end   = today
        default_start = today - timedelta(weeks=4)
        date_range = st.date_input(
            "분석 기간",
            value=(default_start, default_end),
            max_value=today,
            key="period_range",
            label_visibility="collapsed",
        )

        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            sel_start, sel_end = date_range
        else:
            sel_start = sel_end = date_range if isinstance(date_range, date) else today

        weeks_preview = get_weeks(sel_start, sel_end)
        period_logs_preview = [
            l for l in all_logs
            if sel_start.isoformat() <= l['date'] <= sel_end.isoformat()
        ]
        st.caption(
            f"{len(weeks_preview)}주 · 일지 {len(period_logs_preview)}건"
        )

        if st.button("📥 보고서 불러오기", type="primary", use_container_width=True):
            if not period_logs_preview:
                st.warning("해당 기간에 업무일지가 없습니다.")
            else:
                with st.spinner("기간 보고서 분석 중..."):
                    ctx, meta = build_period_context(sel_start, sel_end)
                    st.session_state['period_context'] = ctx
                    st.session_state['period_meta']    = meta
                    st.session_state['chat_history']   = []
                st.rerun()

    # ── 로드된 기간 요약 ──────────────────────────────────────
    meta = st.session_state['period_meta']
    if meta:
        with st.container(border=True):
            st.markdown("**📋 로드된 보고서**")
            st.markdown(
                f"<div style='font-size:0.85rem;line-height:1.8'>"
                f"기간: <b>{meta['start']}</b> ~ <b>{meta['end']}</b><br>"
                f"주차: <b>{meta['weeks']}주</b> &nbsp;|&nbsp; 일지: <b>{meta['log_count']}건</b><br>"
                f"프로젝트: <b>{meta['project_count']}개</b></div>",
                unsafe_allow_html=True,
            )
            for pname in meta['projects']:
                st.markdown(
                    f"<span style='background:#EFF6FF;color:#1d4ed8;padding:2px 8px;"
                    f"border-radius:10px;font-size:0.75rem;margin:2px 2px;display:inline-block'>"
                    f"{pname}</span>",
                    unsafe_allow_html=True,
                )
            if meta['has_ai_summary']:
                st.caption("✦ AI 요약 포함")

    # ── 추천 질문 ─────────────────────────────────────────────
    if st.session_state['period_context']:
        with st.container(border=True):
            st.markdown("**💡 추천 질문**")
            suggested = [
                "각 프로젝트의 진척 현황을 요약해줘",
                "팀원별 투입 공수와 주요 작업은?",
                "주차별로 어떤 작업이 수행됐어?",
                "가장 많은 작업을 한 팀원은 누구야?",
                "이 기간 동안 완료된 주요 성과는?",
                "지연 또는 리스크가 있는 항목이 있어?",
                "다음 단계로 예상되는 작업은?",
            ]
            for q in suggested:
                if st.button(q, key=f"sq_{q[:8]}", use_container_width=True):
                    _ctx = st.session_state['period_context']
                    st.session_state['chat_history'].append({'role': 'user', 'content': q})
                    with st.spinner("답변 생성 중..."):
                        try:
                            ans = chat_response(st.session_state['chat_history'], _ctx)
                            st.session_state['chat_history'].append(
                                {'role': 'assistant', 'content': ans}
                            )
                        except Exception as e:
                            st.session_state['chat_history'].append(
                                {'role': 'assistant', 'content': f"오류: {e}"}
                            )
                    st.rerun()

    # ── 대화 초기화 ───────────────────────────────────────────
    if st.session_state['chat_history']:
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state['chat_history'] = []
            st.rerun()


# ═══════════════════════════════════════════════════
# 우측: 채팅 인터페이스
# ═══════════════════════════════════════════════════
with right:
    chat_area = st.container(height=540)

    with chat_area:
        ctx_loaded = st.session_state['period_context'] is not None
        meta       = st.session_state['period_meta']

        if not st.session_state['chat_history']:
            with st.chat_message("assistant"):
                if ctx_loaded and meta:
                    st.markdown(
                        f"**{meta['start']} ~ {meta['end']}** 기간의 업무 보고서를 불러왔습니다. ✅\n\n"
                        f"- 분석 기간: **{meta['weeks']}주**\n"
                        f"- 업무일지: **{meta['log_count']}건**\n"
                        f"- 대상 프로젝트: **{', '.join(meta['projects'])}**\n\n"
                        "이 기간의 업무 현황, 팀원별 작업, 진척 변화 등 무엇이든 질문해 주세요!"
                    )
                else:
                    st.markdown(
                        "안녕하세요! 업무일지 AI 어시스턴트입니다. 🤖\n\n"
                        "**왼쪽 패널에서 분석할 기간을 선택하고 '보고서 불러오기'를 클릭하면**\n"
                        "해당 기간의 업무 보고서를 기반으로 질의응답을 시작할 수 있습니다.\n\n"
                        "> 💡 주간 AI 요약이 생성되어 있으면 요약 내용도 함께 제공됩니다."
                    )

        for msg in st.session_state['chat_history']:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

    # ── 입력창 ────────────────────────────────────────────────
    disabled = st.session_state['period_context'] is None
    placeholder = (
        "질문을 입력하세요... (예: 2주차에 이개발님이 한 작업은?)"
        if not disabled else
        "먼저 왼쪽에서 기간을 선택하고 '보고서 불러오기'를 눌러주세요"
    )

    if user_input := st.chat_input(placeholder, disabled=disabled):
        _ctx = st.session_state['period_context']
        st.session_state['chat_history'].append({'role': 'user', 'content': user_input})

        with st.spinner("답변 생성 중..."):
            try:
                ans = chat_response(st.session_state['chat_history'], _ctx)
                st.session_state['chat_history'].append(
                    {'role': 'assistant', 'content': ans}
                )
            except Exception as e:
                st.session_state['chat_history'].append(
                    {'role': 'assistant', 'content': f"오류가 발생했습니다: {e}"}
                )

        st.rerun()
