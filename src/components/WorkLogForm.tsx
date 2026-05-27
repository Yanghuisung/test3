import { useEffect, useState, useMemo, type FormEvent, type KeyboardEvent, type ReactElement } from 'react';
import { Link } from 'react-router-dom';
import type { Project, Member } from '../types';

const PRESETS = ['회의', '개발', '검토', '보고', '테스트', '설계', '분석', '문서화', '배포'];

export interface WorkLogFormData {
  projectId: string;
  memberId: string;
  date: string;
  items: string[];
  hours?: number;
  progress?: number;
}

interface Props {
  projects: Project[];
  members: Member[];
  initialProjectId?: string;
  initialMemberId?: string;
  initialDate?: string;
  initialItems?: string[];
  initialHours?: string;
  initialProgress?: string;
  onSubmit: (data: WorkLogFormData) => void;
  cancelHref: string;
}

const WorkLogForm = ({
  projects,
  members,
  initialProjectId = '',
  initialMemberId = '',
  initialDate = '',
  initialItems,
  initialHours = '',
  initialProgress = '',
  onSubmit,
  cancelHref,
}: Props): ReactElement => {
  const [projectId, setProjectId] = useState(initialProjectId);
  const [memberId, setMemberId] = useState(initialMemberId);
  const [date, setDate] = useState(initialDate);
  const [hours, setHours] = useState(initialHours);
  const [progress, setProgress] = useState(initialProgress);
  const [items, setItems] = useState<string[]>(initialItems ?? ['']);

  const selectedProject = useMemo(() => projects.find((p) => p.id === projectId), [projects, projectId]);
  const eligibleMembers = useMemo(() => {
    if (!selectedProject || selectedProject.memberIds.length === 0) return members;
    return members.filter((m) => selectedProject.memberIds.includes(m.id));
  }, [selectedProject, members]);

  useEffect(() => {
    if (memberId && !eligibleMembers.some((m) => m.id === memberId)) {
      setMemberId('');
    }
  }, [eligibleMembers, memberId]);

  const updateItem = (i: number, v: string) => setItems((prev) => prev.map((x, idx) => (idx === i ? v : x)));
  const addItem = () => setItems((prev) => [...prev, '']);
  const removeItem = (i: number) => setItems((prev) => (prev.length === 1 ? [''] : prev.filter((_, idx) => idx !== i)));
  const handleItemKey = (e: KeyboardEvent<HTMLInputElement>, i: number) => {
    if (e.key === 'Enter') { e.preventDefault(); if (i === items.length - 1) addItem(); }
  };
  const addPreset = (preset: string) => {
    setItems((prev) => {
      const last = prev[prev.length - 1];
      return last.trim() === '' ? [...prev.slice(0, -1), preset] : [...prev, preset];
    });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!projectId) { alert('프로젝트를 선택해 주세요.'); return; }
    if (!memberId) { alert('작성자를 선택해 주세요.'); return; }
    const cleaned = items.map((x) => x.trim()).filter(Boolean);
    if (cleaned.length === 0) { alert('최소 하나의 항목을 입력해 주세요.'); return; }
    const hoursNum = hours.trim() === '' ? undefined : Number(hours);
    if (hoursNum !== undefined && (Number.isNaN(hoursNum) || hoursNum < 0)) { alert('공수는 0 이상의 숫자입니다.'); return; }
    const progNum = progress.trim() === '' ? undefined : Number(progress);
    if (progNum !== undefined && (Number.isNaN(progNum) || progNum < 0 || progNum > 100)) { alert('진척률은 0~100 범위입니다.'); return; }
    onSubmit({ projectId, memberId, date, items: cleaned, hours: hoursNum, progress: progNum });
  };

  return (
    <form className="wl-form" onSubmit={handleSubmit}>
      <div className="wl-field-row">
        <div className="wl-field">
          <label>프로젝트 *</label>
          <select value={projectId} onChange={(e) => setProjectId(e.target.value)} required>
            <option value="">선택…</option>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div className="wl-field">
          <label>작성자 *</label>
          <select value={memberId} onChange={(e) => setMemberId(e.target.value)} required>
            <option value="">선택…</option>
            {eligibleMembers.map((m) => <option key={m.id} value={m.id}>{m.name}{m.role ? ` (${m.role})` : ''}</option>)}
          </select>
        </div>
        <div className="wl-field">
          <label>일자 *</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </div>
      </div>

      <div className="wl-field">
        <label>작업 항목 (개조식, 항목당 한 줄)</label>
        <div className="wl-presets">
          {PRESETS.map((p) => (
            <button type="button" key={p} className="wl-preset-tag" onClick={() => addPreset(p)}>{p}</button>
          ))}
        </div>
        <div className="wl-items">
          {items.map((it, i) => (
            <div className="wl-item-row" key={i}>
              <input
                type="text"
                value={it}
                placeholder="예: 요구사항 정의 회의 진행"
                onChange={(e) => updateItem(i, e.target.value)}
                onKeyDown={(e) => handleItemKey(e, i)}
              />
              <button type="button" className="wl-item-remove" onClick={() => removeItem(i)} aria-label="항목 제거">×</button>
            </div>
          ))}
          <button type="button" className="wl-btn wl-btn-sm" onClick={addItem} style={{ alignSelf: 'flex-start' }}>+ 항목 추가</button>
        </div>
      </div>

      <div className="wl-field-row">
        <div className="wl-field">
          <label>공수 (시간)</label>
          <input type="number" min="0" step="0.5" value={hours} onChange={(e) => setHours(e.target.value)} placeholder="예: 6" />
        </div>
        <div className="wl-field">
          <label>진척률 (%) — 선택</label>
          <input type="number" min="0" max="100" step="1" value={progress} onChange={(e) => setProgress(e.target.value)} placeholder="0~100" />
        </div>
      </div>

      <div className="wl-form-actions">
        <button type="submit" className="wl-btn wl-btn-primary">저장</button>
        <Link to={cancelHref} className="wl-btn">취소</Link>
      </div>
    </form>
  );
};

export default WorkLogForm;
