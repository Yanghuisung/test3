import streamlit as st
from datetime import date
from utils.db import list_projects, list_members, list_logs, save_log, delete_log
from utils.style import apply_styles, page_header

st.set_page_config(page_title="업무일지", page_icon="📝", layout="wide")
apply_styles()
page_header("📝", "업무일지")

PRESETS = [
    '요구사항 분석', '설계 검토', '코드 리뷰', '기능 개발', '버그 수정',
    '테스트 작성', '문서 작성', '회의 참석', '배포 작업', '성능 개선',
    '데이터 분석', '인프라 구성', '보안 검토', '고객 대응', '교육/세미나',
]

projects = list_projects()
members = list_members()
project_map = {p['id']: p for p in projects}
member_map = {m['id']: m for m in members}
current_user_id = st.session_state.get('current_user_id', '')
current_user = member_map.get(current_user_id, {})
is_pm = (current_user.get('role') or '').upper() == 'PM'


def log_form(key: str, existing: dict | None = None, default_project_id: str = ''):
    is_edit = existing is not None
    form_proj_id = existing['project_id'] if is_edit else (default_project_id or (projects[0]['id'] if projects else ''))

    with st.form(key=key, clear_on_submit=True):
        # 프로젝트 선택
        proj_ids = [p['id'] for p in projects]
        proj_idx = proj_ids.index(form_proj_id) if form_proj_id in proj_ids else 0
        selected_proj_id = st.selectbox(
            "프로젝트 *",
            options=proj_ids,
            index=proj_idx,
            format_func=lambda x: project_map[x]['name'],
        )

        # 팀원 선택 (PM은 전체, 일반은 자신만)
        proj = project_map.get(selected_proj_id, {})
        eligible_ids = proj.get('member_ids') or [m['id'] for m in members]
        if not is_pm and current_user_id:
            eligible_ids = [current_user_id] if current_user_id in eligible_ids else eligible_ids

        member_idx = 0
        if is_edit and existing['member_id'] in eligible_ids:
            member_idx = eligible_ids.index(existing['member_id'])
        elif current_user_id in eligible_ids:
            member_idx = eligible_ids.index(current_user_id)

        selected_member_id = st.selectbox(
            "작성자 *",
            options=eligible_ids,
            index=member_idx,
            format_func=lambda x: member_map[x]['name'] if x in member_map else x,
        )

        log_date = st.date_input(
            "날짜 *",
            value=date.fromisoformat(existing['date']) if is_edit else date.today(),
        )

        # 업무 항목
        st.markdown("**업무 항목 ***")
        preset_selected = st.multiselect(
            "프리셋에서 선택",
            options=PRESETS,
            default=[it for it in (existing.get('items') or []) if it in PRESETS] if is_edit else [],
        )
        custom_items_str = st.text_area(
            "직접 입력 (한 줄에 하나씩)",
            value="\n".join(it for it in (existing.get('items') or []) if it not in PRESETS) if is_edit else '',
            height=80,
        )

        col1, col2 = st.columns(2)
        hours = col1.number_input(
            "투입 공수 (시간)",
            min_value=0.0, max_value=24.0, step=0.5,
            value=float(existing['hours']) if (is_edit and existing.get('hours') is not None) else 0.0,
        )
        progress = col2.slider(
            "진척률 (%)",
            0, 100,
            value=int(existing['progress']) if (is_edit and existing.get('progress') is not None) else 0,
        )

        submitted = st.form_submit_button("저장", type="primary")
        if submitted:
            custom = [it.strip() for it in custom_items_str.splitlines() if it.strip()]
            all_items = preset_selected + [it for it in custom if it not in preset_selected]
            if not all_items:
                st.error("업무 항목을 하나 이상 입력해주세요.")
                return False
            data = {
                'project_id': selected_proj_id,
                'member_id': selected_member_id,
                'date': log_date.isoformat(),
                'items': all_items,
                'hours': hours if hours > 0 else None,
                'progress': progress,
            }
            if is_edit:
                data['id'] = existing['id']
            try:
                save_log(data)
                st.success("저장되었습니다.")
                return True
            except Exception as e:
                st.error(f"저장 실패: {e}")
    return False


# ── 필터 ──────────────────────────────────────────────────────
with st.expander("🔍 필터", expanded=True):
    fc1, fc2, fc3, fc4 = st.columns(4)
    filter_proj = fc1.selectbox(
        "프로젝트",
        options=[''] + [p['id'] for p in projects],
        format_func=lambda x: '전체' if not x else project_map[x]['name'],
    )
    filter_member = fc2.selectbox(
        "팀원",
        options=[''] + [m['id'] for m in members],
        format_func=lambda x: '전체' if not x else member_map[x]['name'],
    )
    filter_start = fc3.date_input("시작일", value=None)
    filter_end = fc4.date_input("종료일", value=None)

# ── 새 일지 추가 ──────────────────────────────────────────────
with st.expander("➕ 새 업무일지 작성"):
    if log_form('new_log', default_project_id=filter_proj):
        st.rerun()

# ── 일지 목록 ─────────────────────────────────────────────────
all_logs = list_logs()

# Apply filters
filtered = all_logs
if filter_proj:
    filtered = [l for l in filtered if l['project_id'] == filter_proj]
if filter_member:
    filtered = [l for l in filtered if l['member_id'] == filter_member]
if filter_start:
    filtered = [l for l in filtered if l['date'] >= filter_start.isoformat()]
if filter_end:
    filtered = [l for l in filtered if l['date'] <= filter_end.isoformat()]

# PM이 아닌 경우 자신의 일지만
if not is_pm and current_user_id:
    filtered = [l for l in filtered if l['member_id'] == current_user_id]

st.caption(f"총 {len(filtered)}건")

if not filtered:
    st.info("조건에 맞는 업무일지가 없습니다.")
else:
    for l in filtered:
        proj = project_map.get(l['project_id'], {})
        member = member_map.get(l['member_id'], {})
        items_str = " / ".join(l.get('items') or [])
        hours = l.get('hours')
        prog = l.get('progress')

        with st.expander(
            f"**{l['date']}**  `{proj.get('name', '?')}`  {member.get('name', '?')}  —  {items_str[:50]}{'…' if len(items_str) > 50 else ''}"
        ):
            st.write(f"**업무 항목:** {items_str}")
            meta = []
            if hours:
                meta.append(f"투입 공수: {hours}시간")
            if prog is not None:
                meta.append(f"진척률: {prog}%")
            if meta:
                st.caption("  |  ".join(meta))

            can_edit = is_pm or l['member_id'] == current_user_id
            if can_edit:
                col1, col2 = st.columns([1, 1])
                edit_clicked = col1.button("✏️ 수정", key=f"edit_{l['id']}")
                del_clicked = col2.button("🗑️ 삭제", key=f"del_{l['id']}")

                if edit_clicked:
                    st.session_state[f'editing_{l["id"]}'] = not st.session_state.get(f'editing_{l["id"]}', False)
                    st.rerun()

                if st.session_state.get(f'editing_{l["id"]}'):
                    st.markdown("---")
                    if log_form(f'edit_{l["id"]}', existing=l):
                        del st.session_state[f'editing_{l["id"]}']
                        st.rerun()

                if del_clicked:
                    st.session_state[f'confirm_del_{l["id"]}'] = True

                if st.session_state.get(f'confirm_del_{l["id"]}'):
                    st.warning("이 업무일지를 삭제하시겠습니까?")
                    dc1, dc2 = st.columns(2)
                    if dc1.button("삭제 확인", key=f"confirm_{l['id']}", type="primary"):
                        try:
                            delete_log(l['id'])
                            del st.session_state[f'confirm_del_{l["id"]}']
                            st.rerun()
                        except Exception as e:
                            st.error(f"삭제 실패: {e}")
                    if dc2.button("취소", key=f"cancel_{l['id']}"):
                        del st.session_state[f'confirm_del_{l["id"]}']
                        st.rerun()
