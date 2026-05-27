import streamlit as st
from datetime import date
from utils.db import list_projects, list_members, save_project, delete_project
from utils.helpers import latest_progress
from utils.style import apply_styles, page_header

st.set_page_config(page_title="프로젝트 관리", page_icon="🗂️", layout="wide")
apply_styles()
page_header("🗂️", "프로젝트 관리")

STATUS_MAP = {'active': '🟢 진행 중', 'paused': '🟡 일시정지', 'completed': '⚫ 완료'}
STATUS_KEYS = list(STATUS_MAP.keys())

members = list_members()
member_map = {m['id']: m['name'] for m in members}


def project_form(key: str, existing: dict | None = None):
    is_edit = existing is not None
    with st.form(key=key, clear_on_submit=True):
        name = st.text_input("프로젝트명 *", value=existing.get('name', '') if is_edit else '')
        desc = st.text_area("설명", value=(existing.get('description') or '') if is_edit else '')
        col1, col2 = st.columns(2)
        start_val = date.fromisoformat(existing['start_date']) if is_edit else date.today()
        end_val = date.fromisoformat(existing['end_date']) if (is_edit and existing.get('end_date')) else None
        start = col1.date_input("시작일 *", value=start_val)
        end = col2.date_input("종료일 (선택)", value=end_val)
        status = st.selectbox(
            "상태", STATUS_KEYS,
            index=STATUS_KEYS.index(existing['status']) if is_edit else 0,
            format_func=lambda x: STATUS_MAP[x],
        )
        selected_members = st.multiselect(
            "팀원",
            options=[m['id'] for m in members],
            default=existing.get('member_ids', []) if is_edit else [],
            format_func=lambda x: member_map.get(x, x),
        )
        submitted = st.form_submit_button("저장", type="primary")
        if submitted:
            if not name:
                st.error("프로젝트명을 입력해주세요.")
                return False
            data = {
                'name': name,
                'description': desc or None,
                'start_date': start.isoformat(),
                'end_date': end.isoformat() if end else None,
                'status': status,
                'member_ids': selected_members,
            }
            if is_edit:
                data['id'] = existing['id']
            try:
                save_project(data)
                st.success("저장되었습니다.")
                return True
            except Exception as e:
                st.error(f"저장 실패: {e}")
    return False


# ── 새 프로젝트 추가 ──────────────────────────────────────────
with st.expander("➕ 새 프로젝트 추가", expanded=st.session_state.get('open_new_proj', False)):
    if project_form('new_project'):
        st.session_state['open_new_proj'] = False
        st.rerun()

# ── 프로젝트 목록 ─────────────────────────────────────────────
projects = list_projects()
from utils.db import list_logs
all_logs = list_logs()

if not projects:
    st.info("등록된 프로젝트가 없습니다.")
else:
    for p in projects:
        p_logs = [l for l in all_logs if l['project_id'] == p['id']]
        prog = latest_progress(p_logs)
        status_label = STATUS_MAP.get(p['status'], p['status'])
        m_names = [member_map.get(mid, mid) for mid in (p.get('member_ids') or [])]

        with st.expander(f"{status_label}  **{p['name']}**  — 진척률 {prog}%"):
            if p.get('description'):
                st.write(p['description'])
            st.caption(f"기간: {p['start_date']} ~ {p.get('end_date') or '미정'}")
            if m_names:
                st.caption(f"팀원: {', '.join(m_names)}")
            st.progress(prog / 100)

            col1, col2 = st.columns([1, 1])
            edit_clicked = col1.button("✏️ 수정", key=f"edit_{p['id']}")
            del_clicked = col2.button("🗑️ 삭제", key=f"del_{p['id']}")

            if edit_clicked:
                st.session_state[f'editing_{p["id"]}'] = not st.session_state.get(f'editing_{p["id"]}', False)
                st.rerun()

            if st.session_state.get(f'editing_{p["id"]}'):
                st.markdown("---")
                if project_form(f'edit_{p["id"]}', existing=p):
                    del st.session_state[f'editing_{p["id"]}']
                    st.rerun()

            if del_clicked:
                st.session_state[f'confirm_del_{p["id"]}'] = True

            if st.session_state.get(f'confirm_del_{p["id"]}'):
                st.warning(f"**'{p['name']}'** 프로젝트를 삭제하시겠습니까? (연결된 업무일지도 삭제됩니다)")
                dc1, dc2 = st.columns(2)
                if dc1.button("삭제 확인", key=f"confirm_{p['id']}", type="primary"):
                    try:
                        delete_project(p['id'])
                        del st.session_state[f'confirm_del_{p["id"]}']
                        st.rerun()
                    except Exception as e:
                        st.error(f"삭제 실패: {e}")
                if dc2.button("취소", key=f"cancel_{p['id']}"):
                    del st.session_state[f'confirm_del_{p["id"]}']
                    st.rerun()
