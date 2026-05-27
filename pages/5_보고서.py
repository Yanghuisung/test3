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

# ── 컨트롤 ────────────────────────────────────────────────────
cc1, cc2, cc3, cc4 = st.columns([2, 1, 1, 3])
range_type = cc1.radio("기간", ['weekly', 'monthly'],
                       format_func=lambda x: '주간' if x == 'weekly' else '월간',
                       horizontal=True)

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
    end_date = end_of_week(anchor)
    range_label_str = '주간'
    period_label = week_label(anchor)
else:
    start_date = start_of_month(anchor)
    end_date = end_of_month(anchor)
    range_label_str = '월간'
    period_label = month_label(anchor)

start_str = start_date.isoformat()
end_str = end_date.isoformat()
cc4.markdown(f"**{period_label}**  \n{start_str} ~ {end_str}")

# 주간: 프로젝트 반드시 선택 (전체 옵션 없음)
selected_proj = ''
if range_type == 'weekly':
    projects_all = list_projects()
    if not projects_all:
        st.warning("등록된 프로젝트가 없습니다.")
        st.stop()
    proj_ids = [p['id'] for p in projects_all]
    if 'weekly_proj' not in st.session_state or st.session_state['weekly_proj'] not in proj_ids:
        st.session_state['weekly_proj'] = proj_ids[0]
    selected_proj = st.selectbox(
        "프로젝트 선택",
        options=proj_ids,
        format_func=lambda x: next((p['name'] for p in projects_all if p['id'] == x), x),
        key='weekly_proj',
    )

st.divider()

# ── 데이터 로드 ───────────────────────────────────────────────
projects = list_projects()
all_logs = list_logs()
summaries = list_summaries_for_period(range_type, start_str, end_str)
summary_map = {s['project_key']: s for s in summaries}
today_str = date.today().isoformat()

# ── AI 요약 생성/삭제 함수 ────────────────────────────────────
def do_generate(project_key: str, display_name: str, items: list[str]):
    with st.spinner(f"AI 요약 생성 중..."):
        try:
            content = generate_report_summary(
                range_label_str, start_str, end_str, display_name, items)
            save_summary(project_key, range_type, start_str, end_str, content)
            st.success("AI 요약이 생성되었습니다.")
            st.rerun()
        except Exception as e:
            st.error(f"AI 요약 생성 실패: {e}")

def do_delete(project_key: str):
    existing = summary_map.get(project_key)
    if not existing:
        return
    try:
        delete_summary(existing['id'])
        st.rerun()
    except Exception as e:
        st.error(f"삭제 실패: {e}")

# ════════════════════════════════════════════════════════════
# 주간: 프로젝트별 개별 보고서
# ════════════════════════════════════════════════════════════
if range_type == 'weekly':
    target_projects = [p for p in projects if p['id'] == selected_proj]
    has_content = False

    for p in target_projects:
        p_logs = [l for l in all_logs if l['project_id'] == p['id']]
        in_range = [l for l in p_logs if start_str <= l['date'] <= end_str]
        if not in_range:
            continue

        has_content = True
        prog = latest_progress(p_logs)
        all_items = list(dict.fromkeys(
            it.strip() for l in in_range for it in (l.get('items') or []) if it.strip()
        ))
        existing = summary_map.get(p['id'])

        with st.container(border=True):
            h1, h2 = st.columns([4, 1])
            h1.markdown(f"### {p['name']}")
            h2.metric("진척률", f"{prog}%")
            st.progress(prog / 100)

            if existing:
                st.markdown("**📌 AI 요약**")
                for line in existing['content'].split('\n'):
                    if line.strip():
                        st.markdown(line)
                st.caption(f"생성일시: {existing['created_at'][:19].replace('T', ' ')}")
            else:
                st.markdown("**업무 항목**")
                for it in all_items:
                    st.markdown(f"- {it}")

            bc1, bc2 = st.columns([1, 4])
            if existing:
                if bc1.button("↺ 재생성", key=f"regen_{p['id']}"):
                    do_generate(p['id'], p['name'], all_items)
                if bc2.button("원본으로 복원", key=f"restore_{p['id']}"):
                    do_delete(p['id'])
            else:
                if bc1.button("✦ AI 요약 생성", key=f"gen_{p['id']}", type="primary"):
                    do_generate(p['id'], p['name'], all_items)

    if not has_content:
        st.info(f"해당 기간({start_str} ~ {end_str})에 업무일지가 없습니다.")
        st.stop()

# ════════════════════════════════════════════════════════════
# 월간: 전체 프로젝트 통합 보고서
# ════════════════════════════════════════════════════════════
else:
    # 모든 프로젝트의 항목을 하나로 통합
    combined_items = []
    project_sections = []  # 인쇄용 (프로젝트별 구조 유지)
    has_content = False

    for p in projects:
        p_logs = [l for l in all_logs if l['project_id'] == p['id']]
        in_range = [l for l in p_logs if start_str <= l['date'] <= end_str]
        if not in_range:
            continue
        has_content = True
        prog = latest_progress(p_logs)
        items = list(dict.fromkeys(
            it.strip() for l in in_range for it in (l.get('items') or []) if it.strip()
        ))
        combined_items.extend(items)
        project_sections.append({'project': p, 'items': items, 'progress': prog})

    if not has_content:
        st.info(f"해당 기간({start_str} ~ {end_str})에 업무일지가 없습니다.")
        st.stop()

    # 중복 제거
    combined_items = list(dict.fromkeys(combined_items))
    existing = summary_map.get('ALL')

    with st.container(border=True):
        st.markdown(f"### {period_label} 종합 업무 보고서")
        st.caption(f"프로젝트 {len(project_sections)}개 · 업무 항목 {len(combined_items)}건")

        # 프로젝트별 현황 요약
        for sec in project_sections:
            p = sec['project']
            prog = sec['progress']
            st.markdown(f"**{p['name']}** — 진척률 {prog}%")
            st.progress(prog / 100)

        st.divider()

        if existing:
            st.markdown("**📌 AI 요약**")
            for line in existing['content'].split('\n'):
                if line.strip():
                    st.markdown(line)
            st.caption(f"생성일시: {existing['created_at'][:19].replace('T', ' ')}")
        else:
            st.markdown("**전체 업무 항목**")
            for it in combined_items:
                st.markdown(f"- {it}")

        bc1, bc2 = st.columns([1, 4])
        if existing:
            if bc1.button("↺ 재생성", key="regen_ALL"):
                do_generate('ALL', f'{period_label} 전체 프로젝트', combined_items)
            if bc2.button("원본으로 복원", key="restore_ALL"):
                do_delete('ALL')
        else:
            if bc1.button("✦ AI 요약 생성", key="gen_ALL", type="primary"):
                do_generate('ALL', f'{period_label} 전체 프로젝트', combined_items)

# ── 인쇄용 미리보기 ───────────────────────────────────────────
with st.expander("🖨️ 인쇄용 미리보기 / PDF 저장"):
    if range_type == 'weekly':
        # 주간: 선택된 단일 프로젝트 보고서
        target = [p for p in projects if p['id'] == selected_proj]
        sections_html = ""
        for p in target:
            p_logs = [l for l in all_logs if l['project_id'] == p['id']]
            in_range = [l for l in p_logs if start_str <= l['date'] <= end_str]
            if not in_range:
                continue
            prog = latest_progress(p_logs)
            items = list(dict.fromkeys(
                it.strip() for l in in_range for it in (l.get('items') or []) if it.strip()
            ))
            ex = summary_map.get(p['id'])
            if ex:
                body_html = "".join(
                    f"<p style='margin:0 0 4px 0'>{line}</p>"
                    for line in ex['content'].split('\n') if line.strip()
                )
            else:
                body_html = "<ul style='margin:0 0 0 20px;padding:0'>" + \
                    "".join(f"<li>{it}</li>" for it in items) + "</ul>"
            fill = max(0, min(100, prog))
            sections_html += f"""
            <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #e2e8f0;">
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:12.5pt;font-weight:700;color:#0F1B33">{p['name']}</span>
                <span style="font-size:9.5pt;color:#4A5A7C;background:#f0f2f8;border:1px solid #dde2ee;border-radius:4px;padding:2px 10px">진척률 {prog}%</span>
              </div>
              <div style="height:5px;background:#e2e8f0;border-radius:3px;margin-bottom:14px;overflow:hidden">
                <div style="height:100%;width:{fill}%;background:#1B2A4A;border-radius:3px"></div>
              </div>
              <div style="font-size:10pt;color:#222;line-height:1.85">{body_html}</div>
            </div>"""
    else:
        # 월간: 통합 단일 섹션
        ex = summary_map.get('ALL')
        proj_status = "".join(
            f"<li><b>{s['project']['name']}</b> — 진척률 {s['progress']}%</li>"
            for s in project_sections
        )
        if ex:
            body_html = "".join(
                f"<p style='margin:0 0 4px 0'>{line}</p>"
                for line in ex['content'].split('\n') if line.strip()
            )
        else:
            body_html = "<ul style='margin:0 0 0 20px;padding:0'>" + \
                "".join(f"<li>{it}</li>" for it in combined_items) + "</ul>"
        sections_html = f"""
        <div style="margin-bottom:20px;">
          <p style="font-size:11pt;font-weight:700;color:#0F1B33;margin-bottom:8px">프로젝트 현황</p>
          <ul style="margin:0 0 16px 20px;font-size:10pt">{proj_status}</ul>
          <p style="font-size:11pt;font-weight:700;color:#0F1B33;margin-bottom:8px">종합 업무 내용</p>
          <div style="font-size:10pt;color:#222;line-height:1.85">{body_html}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body{{font-family:'Malgun Gothic',sans-serif;font-size:10.5pt;color:#111;line-height:1.7;margin:0;padding:0}}
  .page{{max-width:794px;margin:28px auto;padding:52px 60px;background:#fff;box-shadow:0 4px 32px rgba(0,0,0,.12);min-height:1123px}}
  .title{{font-size:19pt;font-weight:700;letter-spacing:3px;color:#0F1B33;margin:0}}
  .meta{{font-size:9.5pt;color:#4A5A7C;margin-top:6px}}
  .meta div{{margin-bottom:2px}}
  table.approval{{border-collapse:collapse;width:270px;flex-shrink:0}}
  table.approval th{{background:#1B2A4A;color:#fff;font-size:9pt;font-weight:600;text-align:center;padding:7px 0;border:1.5px solid #1B2A4A;letter-spacing:2px;width:90px}}
  table.approval td{{height:80px;border:1.5px solid #1B2A4A;border-top:none}}
  hr.divider{{border:none;border-top:2.5px solid #1B2A4A;margin:4px 0 22px}}
  .footer{{margin-top:48px;text-align:center;font-size:8.5pt;color:#9ca3af;border-top:1px solid #e2e8f0;padding-top:10px}}
  @media print{{.page{{margin:0;box-shadow:none}} button{{display:none}}}}
</style>
</head><body>
<div class="page">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:24px;margin-bottom:20px">
    <div>
      <p class="title">{range_label_str} 업무 보고서</p>
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
  <div class="footer">본 보고서는 업무일지 관리 시스템에서 자동 생성되었습니다. · 생성일시 {today_str}</div>
</div>
<script>
  var btn = document.createElement('button');
  btn.innerText = '🖨️ 인쇄 / PDF 저장';
  btn.style.cssText = 'position:fixed;top:12px;right:12px;padding:8px 16px;background:#1B2A4A;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;z-index:999';
  btn.onclick = function(){{ window.print(); }};
  document.body.appendChild(btn);
</script>
</body></html>"""

    components.html(html, height=900, scrolling=True)
