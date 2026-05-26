import { useEffect, useState, type ReactElement, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getProject, listMembers, saveProject, toIsoDate } from '../utils/storage';
import type { Member, ProjectStatus } from '../types';

const statusOptions: { value: ProjectStatus; label: string }[] = [
  { value: 'active', label: '진행' },
  { value: 'paused', label: '보류' },
  { value: 'completed', label: '완료' },
];

const ProjectForm = (): ReactElement => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState(toIsoDate(new Date()));
  const [endDate, setEndDate] = useState('');
  const [status, setStatus] = useState<ProjectStatus>('active');
  const [memberIds, setMemberIds] = useState<string[]>([]);
  const [members, setMembers] = useState<Member[]>([]);

  useEffect(() => {
    setMembers(listMembers());
    if (id) {
      const p = getProject(id);
      if (p) {
        setName(p.name);
        setDescription(p.description ?? '');
        setStartDate(p.startDate);
        setEndDate(p.endDate ?? '');
        setStatus(p.status);
        setMemberIds(p.memberIds);
      }
    }
  }, [id]);

  const toggleMember = (mid: string) => {
    setMemberIds((prev) => prev.includes(mid) ? prev.filter((x) => x !== mid) : [...prev, mid]);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      alert('프로젝트 이름을 입력해 주세요.');
      return;
    }
    const saved = saveProject({
      id,
      name: name.trim(),
      description: description.trim() || undefined,
      startDate,
      endDate: endDate || undefined,
      memberIds,
      status,
    });
    navigate(`/projects/${saved.id}`);
  };

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">{isEdit ? '프로젝트 수정' : '새 프로젝트'}</h1>
          <p className="wl-page-sub">기본 정보와 투입 구성원을 지정합니다.</p>
        </div>
        <Link to="/projects" className="wl-btn">목록으로</Link>
      </div>

      <div className="wl-section">
        <form className="wl-form" onSubmit={handleSubmit}>
          <div className="wl-field">
            <label>프로젝트 이름 *</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="예: 전력계통 해석 솔루션 고도화" required />
          </div>

          <div className="wl-field">
            <label>개요</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="프로젝트 한 줄 설명" />
          </div>

          <div className="wl-field-row">
            <div className="wl-field">
              <label>시작일</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div className="wl-field">
              <label>종료(예정)</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <div className="wl-field">
              <label>상태</label>
              <select value={status} onChange={(e) => setStatus(e.target.value as ProjectStatus)}>
                {statusOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>

          <div className="wl-field">
            <label>투입 구성원</label>
            {members.length === 0 ? (
              <span className="wl-kpi-hint">
                등록된 구성원이 없습니다. <Link to="/members">구성원 관리</Link>에서 먼저 추가하세요.
              </span>
            ) : (
              <div className="wl-chip-list">
                {members.map((m) => {
                  const selected = memberIds.includes(m.id);
                  return (
                    <button
                      type="button"
                      key={m.id}
                      onClick={() => toggleMember(m.id)}
                      className="wl-chip"
                      style={{
                        cursor: 'pointer',
                        background: selected ? 'var(--accent, #1B2A4A)' : undefined,
                        color: selected ? '#fff' : undefined,
                        borderColor: selected ? 'var(--accent, #1B2A4A)' : undefined,
                      }}
                    >
                      {m.name}{m.role ? ` · ${m.role}` : ''}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="wl-form-actions">
            <button type="submit" className="wl-btn wl-btn-primary">{isEdit ? '저장' : '만들기'}</button>
            <Link to="/projects" className="wl-btn">취소</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProjectForm;
