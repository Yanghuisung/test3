import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
from utils.db import (
    list_projects, list_members, list_logs,
    list_summaries_for_period, save_summary, delete_summary,
)
from utils.helpers import (
    start_of_week, end_of_week, start_of_month, end_of_month,
    latest_progress, week_label, month_label,
)
from utils.ai_utils import generate_report_summary
from utils.style import apply_styles, page_header

st.set_page_config(page_title="보고서", page_icon="📄", layout="wide")
apply_styles()
page_header("📄", "업무 보고서")

# ── 기간 컨트롤 ───────────────────────────────────────────────
cc1, cc2, cc3, cc4 = st.columns([2, 1, 1, 3])
range_type = cc1.radio(
    "기간", ['weekly', 'monthly'],
    format_func=lambda x: '주간' if x == 'weekly' else '월간',
    horizontal=True,
)

if 'report_anchor' not in st.session_state:
    st.session_state['report_anchor'] = date.today().isoformat()

anchor = date.fromisoformat(st.session_state['report_anchor'])

if cc2.button("◀ 이전"):
    delta = timedelta(weeks=1) if range_type == 'weekly' else timedelta(days=32)
    st.session_state['report_anchor'] = (anchor - delta).isoformat()
    st.rerun()
if cc3.button("다음 ▶"):
    delta = timedelta(weeks=1) if range_type == 'weekly' else timedelta(days=28)
    st.session_state['report_anchor'] = (anchor + delta).isoformat()
    st.rerun()

if range_type == 'weekly':
    start_date = start_of_week(anchor)
    end_date   = end_of_week(anchor)
    range_label_str = '주간'
    period_label    = week_label(anchor)
else:
    start_date = start_of_month(anchor)
    end_date   = end_of_month(anchor)
    range_label_str = '월간'
    period_label    = month_label(anchor)

start_str  = start_date.isoformat()
end_str    = end_date.isoformat()
today_str  = date.today().isoformat()
cc4.markdown(f"**{period_label}**  \n{start_str} ~ {end_str}")
st.divider()

# ── 데이터 로드 ───────────────────────────────────────────────
projects   = list_projects()
members    = list_members()
member_map = {m['id']: m for m in members}
all_logs   = list_logs()
summaries  = list_summaries_for_period(range_type, start_str, end_str)
summary_map = {s['project_key']: s for s in summaries}


# ── 헬퍼 ─────────────────────────────────────────────────────
def _collect_member_ctx(logs_in_range: list):
    mh: dict[str, float] = {}
    for l in logs_in_range:
        name = member_map.get(l['member_id'], {}).get('name', '미지정')
        mh[name] = mh.get(name, 0) + (l.get('hours') or 0)
    return list(mh.keys()), sum(mh.values()), mh


def _status_badge(progress: int) -> str:
    if progress >= 100:
        return ('<span style="background:#dcfce7;color:#15803d;padding:2px 10px;'
                'border-radius:12px;font-size:0.78rem;font-weight:600">완료</span>')
    return ('<span style="background:#dbeafe;color:#1d4ed8;padding:2px 10px;'
            'border-radius:12px;font-size:0.78rem;font-weight:600">진행 중</span>')


def _team_bar(mh: dict) -> str:
    parts = " &nbsp;|&nbsp; ".join(
        f"<b>{n}</b>&nbsp;{h}h"
        for n, h in sorted(mh.items(), key=lambda x: -x[1])
    )
    return (f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;'
            f'padding:6px 14px;margin:6px 0 10px;font-size:0.85rem">👥 {parts}</div>')


def _print_html(sections_html: str, label: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body{{font-family:'Malgun Gothic',sans-serif;font-size:10.5pt;color:#111;line-height:1.7;margin:0;padding:0}}
  .page{{max-width:794px;margin:28px auto;padding:52px 60px;background:#fff;
         box-shadow:0 4px 32px rgba(0,0,0,.12);min-height:1123px}}
  .title{{font-size:19pt;font-weight:700;letter-spacing:3px;color:#0F1B33;margin:0}}
  .meta{{font-size:9.5pt;color:#4A5A7C;margin-top:6px}}
  table.approval{{border-collapse:collapse;width:270px;flex-shrink:0}}
  table.approval th{{background:#1B2A4A;color:#fff;font-size:9pt;font-weight:600;
                    text-align:center;padding:7px 0;border:1.5px solid #1B2A4A;
                    letter-spacing:2px;width:90px}}
  table.approval td{{height:80px;border:1.5px solid #1B2A4A;border-top:none}}
  hr.divider{{border:none;border-top:2.5px solid #1B2A4A;margin:4px 0 22px}}
  .footer{{margin-top:48px;text-align:center;font-size:8.5pt;color:#9ca3af;
           border-top:1px solid #e2e8f0;padding-top:10px}}
  @media print{{.page{{margin:0;box-shadow:none}} button{{display:none}}}}
</style></head><body>
<div class="page">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;
              gap:24px;margin-bottom:20px">
    <div>
      <p class="title">{label} 업무 보고서</p>
      <div class="meta">
        <div>보고 기간 : {start_str} ~ {end_str}</div>
        <div>작 성 일 &nbsp;: {today_str}</div>
      </div>
    </div>
    <table class="approval">
      <thead><tr><th>작 성</th><th>검 토</th><th>승 인</th></tr></thead>
      <tbody><tr><td></td><td></td><td></td></tr></tbody>
    </table>
  </div>
  <hr class="divider">
  {sections_html}
  <div class="footer">
    본 보고서는 업무일지 관리 시스템에서 자동 생성되었습니다. · 생성일시 {today_str}
  </div>
</div>
<script>
  var btn = document.createElement('button');
  btn.innerText = '🖨️ 인쇄 / PDF 저장';
  btn.style.cssText = 'position:fixed;top:12px;right:12px;padding:8px 16px;'
    + 'background:#1B2A4A;color:#fff;border:none;border-radius:6px;cursor:pointer;'
    + 'font-size:14px;z-index:999';
  btn.onclick = function(){{ window.print(); }};
  document.body.appendChild(btn);
</script>
</body></html>"""


def do_generate(project_key, display_name, items,
                members_list=None, progress=None,
                total_hours=None, member_hours=None):
    with st.spinner("AI 요약 생성 중..."):
        try:
            content = generate_report_summary(
                range_label_str, start_str, end_str, display_name, items,
                members=members_list, progress=progress,
                total_hours=total_hours, member_hours=member_hours,
            )
            save_summary(project_key, range_type, start_str, end_str, content)
            st.success("AI 요약이 생성되었습니다.")
            st.rerun()
        except Exception as e:
            st.error(f"AI 요약 생성 실패: {e}")


def do_delete(project_key):
    existing = summary_map.get(project_key)
    if not existing:
        return
    try:
        delete_summary(existing['id'])
        st.rerun()
    except Exception as e:
        st.error(f"삭제 실패: {e}")


# ════════════════════════════════════════════════════════════
# 주간: 프로젝트 테이블 → 팝업
# ════════════════════════════════════════════════════════════
if range_type == 'weekly':

    # 해당 기간 데이터 수집
    weekly_rows = []
    for p in projects:
        p_logs   = [l for l in all_logs if l['project_id'] == p['id']]
        in_range = [l for l in p_logs if start_str <= l['date'] <= end_str]
        if not in_range:
            continue
        prog = latest_progress(p_logs)
        m_names, t_hours, mh = _collect_member_ctx(in_range)
        items = list(dict.fromkeys(
            it.strip() for l in in_range for it in (l.get('items') or []) if it.strip()
        ))
        weekly_rows.append({
            'project': p, 'prog': prog, 'items': items,
            'm_names': m_names, 't_hours': t_hours, 'mh': mh,
        })

    if not weekly_rows:
        st.info(f"해당 기간({start_str} ~ {end_str})에 업무일지가 없습니다.")
        st.stop()

    # ── 테이블 헤더 ──────────────────────────────────────────
    st.markdown("#### 프로젝트 현황")
    h0, h1, h2, h3, h4 = st.columns([4, 1, 2, 3, 1])
    for col, label in zip(
        [h0, h1, h2, h3, h4],
        ["프로젝트명", "진척률", "상태", "참여 팀원", ""],
    ):
        col.markdown(
            f"<span style='font-size:0.75rem;font-weight:700;color:#64748B;"
            f"text-transform:uppercase;letter-spacing:0.6px'>{label}</span>",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="height:2px;background:#E2E8F0;margin:4px 0 4px"></div>',
        unsafe_allow_html=True,
    )

    # ── 테이블 행 ────────────────────────────────────────────
    for row in weekly_rows:
        p           = row['project']
        prog        = row['prog']
        members_str = " · ".join(row['m_names']) or "—"

        c0, c1, c2, c3, c4 = st.columns([4, 1, 2, 3, 1])
        c0.markdown(f"**{p['name']}**")
        c1.markdown(f"`{prog}%`")
        c2.markdown(_status_badge(prog), unsafe_allow_html=True)
        c3.markdown(
            f"<span style='font-size:0.88rem'>{members_str}</span>",
            unsafe_allow_html=True,
        )
        if c4.button("보고서", key=f"open_{p['id']}"):
            st.session_state['weekly_dialog_project'] = p['id']
            st.rerun()

    # ── 팝업 다이얼로그 ──────────────────────────────────────
    if 'weekly_dialog_project' in st.session_state:
        proj_id = st.session_state['weekly_dialog_project']
        row = next((r for r in weekly_rows if r['project']['id'] == proj_id), None)

        if row:
            _p        = row['project']
            _prog     = row['prog']
            _items    = row['items']
            _m_names  = row['m_names']
            _t_hours  = row['t_hours']
            _mh       = row['mh']
            _existing = summary_map.get(_p['id'])

            @st.dialog(f"📄 {_p['name']}", width="large")
            def _weekly_dialog():
                # 상단 메타 정보
                mi1, mi2, mi3 = st.columns(3)
                mi1.metric("보고 기간", f"{start_str[5:]} ~ {end_str[5:]}")
                mi2.metric("진척률", f"{_prog}%")
                mi3.metric("총 공수", f"{_t_hours}h")
                st.progress(_prog / 100)
                st.markdown(_team_bar(_mh), unsafe_allow_html=True)
                st.divider()

                # 요약 또는 업무 항목
                if _existing:
                    st.markdown("**📌 AI 요약**")
                    for line in _existing['content'].split('\n'):
                        if line.strip():
                            st.markdown(line)
                    st.caption(
                        f"생성일시: {_existing['created_at'][:19].replace('T', ' ')}"
                    )
                else:
                    st.markdown("**업무 항목**")
                    for it in _items:
                        st.markdown(f"- {it}")

                st.divider()
                bc1, bc2, _, bc_close = st.columns([2, 2, 3, 1])
                if _existing:
                    if bc1.button("↺ 재생성", key="dlg_regen"):
                        do_generate(
                            _p['id'], _p['name'], _items,
                            _m_names, _prog, _t_hours, _mh,
                        )
                    if bc2.button("원본 복원", key="dlg_restore"):
                        do_delete(_p['id'])
                else:
                    if bc1.button("✦ AI 요약 생성", key="dlg_gen", type="primary"):
                        do_generate(
                            _p['id'], _p['name'], _items,
                            _m_names, _prog, _t_hours, _mh,
                        )
                if bc_close.button("✕ 닫기", key="dlg_close"):
                    del st.session_state['weekly_dialog_project']
                    st.rerun()

            _weekly_dialog()

    # ── 인쇄용 미리보기 ──────────────────────────────────────
    with st.expander("🖨️ 인쇄용 미리보기 / PDF 저장"):
        sel_id    = st.session_state.get('weekly_dialog_project') or weekly_rows[0]['project']['id']
        print_row = next((r for r in weekly_rows if r['project']['id'] == sel_id), weekly_rows[0])
        _p    = print_row['project']
        _prog = print_row['prog']
        _mh   = print_row['mh']
        ex    = summary_map.get(_p['id'])
        if ex:
            body_html = "".join(
                f"<p style='margin:0 0 4px 0'>{line}</p>"
                for line in ex['content'].split('\n') if line.strip()
            )
        else:
            body_html = ("<ul style='margin:0 0 0 20px;padding:0'>"
                         + "".join(f"<li>{it}</li>" for it in print_row['items'])
                         + "</ul>")
        team_info = " / ".join(
            f"{n}({h}h)" for n, h in sorted(_mh.items(), key=lambda x: -x[1])
        )
        fill = max(0, min(100, _prog))
        sections_html = f"""
        <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #e2e8f0;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:12.5pt;font-weight:700;color:#0F1B33">{_p['name']}</span>
            <span style="font-size:9.5pt;color:#4A5A7C;background:#f0f2f8;border:1px solid #dde2ee;
                         border-radius:4px;padding:2px 10px">진척률 {_prog}%</span>
          </div>
          <div style="font-size:8.5pt;color:#6B7280;margin-bottom:6px">참여: {team_info}</div>
          <div style="height:5px;background:#e2e8f0;border-radius:3px;margin-bottom:14px;overflow:hidden">
            <div style="height:100%;width:{fill}%;background:#1B2A4A;border-radius:3px"></div>
          </div>
          <div style="font-size:10pt;color:#222;line-height:1.85">{body_html}</div>
        </div>"""
        components.html(_print_html(sections_html, "주간"), height=900, scrolling=True)


# ════════════════════════════════════════════════════════════
# 월간: 프로젝트별 개별 섹션
# ════════════════════════════════════════════════════════════
else:
    monthly_rows: list[dict] = []
    combined_mh:  dict[str, float] = {}

    for p in projects:
        p_logs   = [l for l in all_logs if l['project_id'] == p['id']]
        in_range = [l for l in p_logs if start_str <= l['date'] <= end_str]
        if not in_range:
            continue
        prog = latest_progress(p_logs)
        m_names, t_hours, mh = _collect_member_ctx(in_range)
        items = list(dict.fromkeys(
            it.strip() for l in in_range for it in (l.get('items') or []) if it.strip()
        ))
        for name, h in mh.items():
            combined_mh[name] = combined_mh.get(name, 0) + h
        monthly_rows.append({
            'project': p, 'prog': prog, 'items': items,
            'm_names': m_names, 't_hours': t_hours, 'mh': mh,
        })

    if not monthly_rows:
        st.info(f"해당 기간({start_str} ~ {end_str})에 업무일지가 없습니다.")
        st.stop()

    total_h = sum(combined_mh.values())
    st.markdown(f"### {period_label} 종합 업무 보고서")
    st.caption(
        f"프로젝트 {len(monthly_rows)}개 &nbsp;·&nbsp; "
        f"참여 인원 {len(combined_mh)}명 &nbsp;·&nbsp; "
        f"총 투입 공수 {total_h}h"
    )
    st.markdown("")

    for row in monthly_rows:
        p        = row['project']
        prog     = row['prog']
        items    = row['items']
        m_names  = row['m_names']
        t_hours  = row['t_hours']
        mh       = row['mh']
        existing = summary_map.get(p['id'])

        with st.container(border=True):
            # 헤더: 프로젝트명 + 상태 배지 + 메트릭
            hc1, hc2, hc3 = st.columns([5, 1, 1])
            hc1.markdown(
                f"**{p['name']}** &nbsp;&nbsp; {_status_badge(prog)}",
                unsafe_allow_html=True,
            )
            hc2.metric("진척률", f"{prog}%")
            hc3.metric("공수", f"{t_hours}h")
            st.progress(prog / 100)

            # 팀원 공수 바
            st.markdown(_team_bar(mh), unsafe_allow_html=True)

            # AI 요약 또는 업무 항목
            if existing:
                st.markdown("**📌 AI 요약**")
                for line in existing['content'].split('\n'):
                    if line.strip():
                        st.markdown(line)
                st.caption(
                    f"생성일시: {existing['created_at'][:19].replace('T', ' ')}"
                )
            else:
                st.markdown("**업무 항목**")
                for it in items:
                    st.markdown(f"- {it}")

            bc1, bc2 = st.columns([1, 4])
            if existing:
                if bc1.button("↺ 재생성", key=f"regen_{p['id']}"):
                    do_generate(p['id'], p['name'], items, m_names, prog, t_hours, mh)
                if bc2.button("원본으로 복원", key=f"restore_{p['id']}"):
                    do_delete(p['id'])
            else:
                if bc1.button("✦ AI 요약 생성", key=f"gen_{p['id']}", type="primary"):
                    do_generate(p['id'], p['name'], items, m_names, prog, t_hours, mh)

    # ── 인쇄용 미리보기 ──────────────────────────────────────
    with st.expander("🖨️ 인쇄용 미리보기 / PDF 저장"):
        sections_html = ""
        for row in monthly_rows:
            p     = row['project']
            prog  = row['prog']
            mh    = row['mh']
            ex    = summary_map.get(p['id'])
            if ex:
                body_html = "".join(
                    f"<p style='margin:0 0 4px 0'>{line}</p>"
                    for line in ex['content'].split('\n') if line.strip()
                )
            else:
                body_html = ("<ul style='margin:0 0 0 20px;padding:0'>"
                             + "".join(f"<li>{it}</li>" for it in row['items'])
                             + "</ul>")
            team_info = " / ".join(
                f"{n}({h}h)" for n, h in sorted(mh.items(), key=lambda x: -x[1])
            )
            fill = max(0, min(100, prog))
            sections_html += f"""
            <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #e2e8f0;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:12.5pt;font-weight:700;color:#0F1B33">{p['name']}</span>
                <span style="font-size:9.5pt;color:#4A5A7C;background:#f0f2f8;border:1px solid #dde2ee;
                             border-radius:4px;padding:2px 10px">진척률 {prog}%</span>
              </div>
              <div style="font-size:8.5pt;color:#6B7280;margin-bottom:6px">참여: {team_info}</div>
              <div style="height:5px;background:#e2e8f0;border-radius:3px;margin-bottom:14px;overflow:hidden">
                <div style="height:100%;width:{fill}%;background:#1B2A4A;border-radius:3px"></div>
              </div>
              <div style="font-size:10pt;color:#222;line-height:1.85">{body_html}</div>
            </div>"""
        components.html(_print_html(sections_html, "월간"), height=900, scrolling=True)
