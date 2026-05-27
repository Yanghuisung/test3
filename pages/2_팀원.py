import streamlit as st
from utils.db import list_members, save_member, delete_member
from utils.style import apply_styles, page_header

st.set_page_config(page_title="팀원 관리", page_icon="👥", layout="wide")
apply_styles()
page_header("👥", "팀원 관리")


def member_form(key: str, existing: dict | None = None):
    is_edit = existing is not None
    with st.form(key=key, clear_on_submit=True):
        name = st.text_input("이름 *", value=existing.get('name', '') if is_edit else '')
        role = st.text_input("역할", value=(existing.get('role') or '') if is_edit else '')
        email = st.text_input("이메일", value=(existing.get('email') or '') if is_edit else '')
        submitted = st.form_submit_button("저장", type="primary")
        if submitted:
            if not name:
                st.error("이름을 입력해주세요.")
                return False
            data = {'name': name, 'role': role or None, 'email': email or None}
            if is_edit:
                data['id'] = existing['id']
            try:
                save_member(data)
                st.success("저장되었습니다.")
                return True
            except Exception as e:
                st.error(f"저장 실패: {e}")
    return False


# ── 새 팀원 추가 ──────────────────────────────────────────────
with st.expander("➕ 새 팀원 추가"):
    if member_form('new_member'):
        st.rerun()

# ── 팀원 목록 ─────────────────────────────────────────────────
members = list_members()

if not members:
    st.info("등록된 팀원이 없습니다.")
else:
    for m in members:
        with st.expander(f"**{m['name']}**  —  {m.get('role') or '역할 미지정'}"):
            if m.get('email'):
                st.caption(f"📧 {m['email']}")
            st.caption(f"등록일: {m.get('created_at', '')[:10]}")

            col1, col2 = st.columns([1, 1])
            edit_clicked = col1.button("✏️ 수정", key=f"edit_{m['id']}")
            del_clicked = col2.button("🗑️ 삭제", key=f"del_{m['id']}")

            if edit_clicked:
                st.session_state[f'editing_{m["id"]}'] = not st.session_state.get(f'editing_{m["id"]}', False)
                st.rerun()

            if st.session_state.get(f'editing_{m["id"]}'):
                st.markdown("---")
                if member_form(f'edit_{m["id"]}', existing=m):
                    del st.session_state[f'editing_{m["id"]}']
                    st.rerun()

            if del_clicked:
                st.session_state[f'confirm_del_{m["id"]}'] = True

            if st.session_state.get(f'confirm_del_{m["id"]}'):
                st.warning(f"**'{m['name']}'** 팀원을 삭제하시겠습니까?")
                dc1, dc2 = st.columns(2)
                if dc1.button("삭제 확인", key=f"confirm_{m['id']}", type="primary"):
                    try:
                        delete_member(m['id'])
                        del st.session_state[f'confirm_del_{m["id"]}']
                        st.rerun()
                    except Exception as e:
                        st.error(f"삭제 실패: {e}")
                if dc2.button("취소", key=f"cancel_{m['id']}"):
                    del st.session_state[f'confirm_del_{m["id"]}']
                    st.rerun()
