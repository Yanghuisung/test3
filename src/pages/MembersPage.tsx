import { useEffect, useState, useCallback, type ReactElement, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { listMembers, saveMember, deleteMember, listProjects } from '../utils/db';
import { useToast } from '../contexts/ToastContext';
import type { Member, Project } from '../types';

const MembersPage = (): ReactElement => {
  const { showToast } = useToast();
  const [members, setMembers] = useState<Member[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [editing, setEditing] = useState<Member | null>(null);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [email, setEmail] = useState('');

  const refresh = useCallback(async () => {
    const [m, p] = await Promise.all([listMembers(), listProjects()]);
    setMembers(m);
    setProjects(p);
  }, []);

  useEffect(() => {
    refresh().catch((err) => { console.error(err); showToast('데이터를 불러오는 중 오류가 발생했습니다.', 'error'); });
  }, [refresh]);

  const resetForm = () => {
    setEditing(null);
    setName('');
    setRole('');
    setEmail('');
  };

  const startEdit = (m: Member) => {
    setEditing(m);
    setName(m.name);
    setRole(m.role ?? '');
    setEmail(m.email ?? '');
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      alert('이름을 입력해 주세요.');
      return;
    }
    saveMember({
      id: editing?.id,
      name: name.trim(),
      role: role.trim() || undefined,
      email: email.trim() || undefined,
    })
      .then(() => {
        showToast(`구성원을 ${editing ? '수정' : '추가'}했습니다.`, 'success');
        resetForm();
        return refresh();
      })
      .catch((err) => { console.error(err); showToast('저장 중 오류가 발생했습니다.', 'error'); });
  };

  const handleDelete = (m: Member) => {
    const projectCount = projects.filter((p) => p.memberIds.includes(m.id)).length;
    const note = projectCount > 0 ? `\n현재 ${projectCount}개 프로젝트에 배정되어 있으며, 해당 배정에서도 제거됩니다.` : '';
    if (!confirm(`"${m.name}"을(를) 삭제할까요?${note}`)) return;
    deleteMember(m.id)
      .then(() => {
        showToast('구성원을 삭제했습니다.', 'success');
        if (editing?.id === m.id) resetForm();
        return refresh();
      })
      .catch((err) => { console.error(err); showToast('삭제 중 오류가 발생했습니다.', 'error'); });
  };

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">구성원</h1>
          <p className="wl-page-sub">프로젝트에 투입될 인원을 관리합니다.</p>
        </div>
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">{editing ? '구성원 수정' : '구성원 추가'}</h2>
        </div>
        <form className="wl-form" onSubmit={handleSubmit}>
          <div className="wl-field-row">
            <div className="wl-field">
              <label>이름 *</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="홍길동" required />
            </div>
            <div className="wl-field">
              <label>역할</label>
              <input type="text" value={role} onChange={(e) => setRole(e.target.value)} list="role-options" placeholder="PM / 팀원 / 개발자" />
              <datalist id="role-options">
                <option value="PM" />
                <option value="팀원" />
                <option value="연구원" />
                <option value="개발자" />
                <option value="기획자" />
                <option value="디자이너" />
                <option value="QA" />
              </datalist>
            </div>
            <div className="wl-field">
              <label>이메일</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="user@kdn.com" />
            </div>
          </div>
          <div className="wl-form-actions">
            <button type="submit" className="wl-btn wl-btn-primary">{editing ? '저장' : '추가'}</button>
            {editing && <button type="button" className="wl-btn" onClick={resetForm}>취소</button>}
          </div>
        </form>
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">구성원 목록 ({members.length})</h2>
        </div>
        {members.length === 0 ? (
          <div className="wl-empty"><p style={{ margin: 0 }}>등록된 구성원이 없습니다.</p></div>
        ) : (
          <table className="wl-table">
            <thead>
              <tr><th>이름</th><th>역할</th><th>이메일</th><th>배정 프로젝트</th><th></th></tr>
            </thead>
            <tbody>
              {members.map((m) => {
                const assigned = projects.filter((p) => p.memberIds.includes(m.id));
                return (
                  <tr key={m.id}>
                    <td style={{ fontWeight: 500 }}>
                      <Link to={`/members/${m.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                        {m.name}
                      </Link>
                    </td>
                    <td>
                      {m.role ? (
                        <span className={`wl-badge ${m.role === 'PM' ? 'wl-badge-pm' : 'wl-badge-role'}`}>{m.role}</span>
                      ) : '—'}
                    </td>
                    <td>{m.email ?? '—'}</td>
                    <td>
                      {assigned.length === 0 ? <span className="wl-kpi-hint">없음</span> : (
                        <div className="wl-chip-list">
                          {assigned.map((p) => (
                            <Link key={p.id} to={`/projects/${p.id}`} className="wl-chip" style={{ textDecoration: 'none', color: 'inherit' }}>
                              {p.name}
                            </Link>
                          ))}
                        </div>
                      )}
                    </td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <button className="wl-btn wl-btn-sm" onClick={() => startEdit(m)}>수정</button>{' '}
                      <button className="wl-btn wl-btn-sm wl-btn-danger" onClick={() => handleDelete(m)}>삭제</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default MembersPage;
