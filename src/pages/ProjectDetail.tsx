import { useEffect, useState, type ReactElement } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  getProject,
  listMembers,
  logsByProject,
  latestProgress,
  progressSeries,
  deleteProject,
  deleteLog,
} from '../utils/storage';
import type { Project, Member, WorkLog } from '../types';

const statusLabel: Record<Project['status'], string> = {
  active: '진행',
  paused: '보류',
  completed: '완료',
};

const ProjectDetail = (): ReactElement => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | undefined>();
  const [members, setMembers] = useState<Member[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);

  const refresh = () => {
    if (!id) return;
    setProject(getProject(id));
    setMembers(listMembers());
    setLogs(logsByProject(id));
  };

  useEffect(refresh, [id]);

  if (!project) {
    return (
      <div className="wl-container">
        <div className="wl-empty">
          <h3>프로젝트를 찾을 수 없습니다</h3>
          <Link to="/projects" className="wl-btn">목록으로</Link>
        </div>
      </div>
    );
  }

  const prog = latestProgress(project.id);
  const series = progressSeries(project.id);

  const handleDelete = () => {
    if (!confirm(`"${project.name}" 프로젝트를 삭제할까요? 관련 일지도 함께 제거됩니다.`)) return;
    deleteProject(project.id);
    navigate('/projects');
  };

  const handleLogDelete = (logId: string) => {
    if (!confirm('이 일지를 삭제할까요?')) return;
    deleteLog(logId);
    refresh();
  };

  // Sparkline
  const W = 600, H = 140, padX = 12, padY = 16;
  let chartPath = '';
  let chartArea = '';
  if (series.length > 0) {
    const xs = series.map((_, i) => padX + (i * (W - 2 * padX)) / Math.max(1, series.length - 1));
    const ys = series.map((p) => H - padY - (p.progress / 100) * (H - 2 * padY));
    chartPath = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${ys[i].toFixed(1)}`).join(' ');
    chartArea = `${chartPath} L ${xs[xs.length - 1].toFixed(1)} ${H - padY} L ${xs[0].toFixed(1)} ${H - padY} Z`;
  }

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">{project.name}</h1>
          <p className="wl-page-sub">
            <span className={`wl-badge wl-badge-${project.status}`}>{statusLabel[project.status]}</span>
            <span style={{ marginLeft: 10 }}>
              {project.startDate}{project.endDate ? ` ~ ${project.endDate}` : ' ~'}
            </span>
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/logs/new" className="wl-btn wl-btn-primary">+ 일지 작성</Link>
          <Link to={`/projects/${project.id}/edit`} className="wl-btn">수정</Link>
          <button className="wl-btn wl-btn-danger" onClick={handleDelete}>삭제</button>
        </div>
      </div>

      {project.description && (
        <div className="wl-section">
          <div className="wl-section-title" style={{ marginBottom: 6 }}>개요</div>
          <p style={{ margin: 0, color: 'var(--text-primary)' }}>{project.description}</p>
        </div>
      )}

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">진척률 추이</h2>
          <span className="wl-trend-progress">현재 {prog}%</span>
        </div>
        {series.length === 0 ? (
          <div className="wl-empty"><p style={{ margin: 0 }}>진척률 데이터가 없습니다. 일지 작성 시 진척률을 입력해 보세요.</p></div>
        ) : (
          <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxHeight: 200, color: 'var(--accent, #1B2A4A)' }}>
            <line x1="0" y1={H - padY} x2={W} y2={H - padY} stroke="currentColor" strokeOpacity="0.2" />
            <line x1="0" y1={padY} x2={W} y2={padY} stroke="currentColor" strokeOpacity="0.08" strokeDasharray="2,4" />
            <path d={chartArea} fill="currentColor" fillOpacity="0.12" />
            <path d={chartPath} fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
            {series.map((p, i) => {
              const x = padX + (i * (W - 2 * padX)) / Math.max(1, series.length - 1);
              const y = H - padY - (p.progress / 100) * (H - 2 * padY);
              return <circle key={i} cx={x} cy={y} r="3" fill="currentColor" />;
            })}
            <text x={padX} y={padY - 4} fontSize="10" fill="currentColor" opacity="0.6">100%</text>
            <text x={padX} y={H - 2} fontSize="10" fill="currentColor" opacity="0.6">0%</text>
          </svg>
        )}
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">참여 구성원</h2>
        </div>
        <div className="wl-chip-list">
          {project.memberIds.length === 0 && <span className="wl-kpi-hint">배정된 구성원이 없습니다.</span>}
          {project.memberIds.map((mid) => {
            const m = members.find((x) => x.id === mid);
            return m ? (
              <span key={mid} className="wl-chip">
                {m.name}{m.role ? ` · ${m.role}` : ''}
              </span>
            ) : null;
          })}
        </div>
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">작성된 일지 ({logs.length})</h2>
          <Link to={`/summary?projectId=${project.id}`} className="wl-btn wl-btn-sm">요약 보기</Link>
        </div>
        {logs.length === 0 ? (
          <div className="wl-empty"><p style={{ margin: 0 }}>작성된 일지가 없습니다.</p></div>
        ) : (
          <table className="wl-table">
            <thead>
              <tr>
                <th>일자</th>
                <th>작성자</th>
                <th>항목</th>
                <th>공수</th>
                <th>진척</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {[...logs].reverse().map((l) => {
                const m = members.find((x) => x.id === l.memberId);
                return (
                  <tr key={l.id}>
                    <td>{l.date}</td>
                    <td>{m?.name ?? '—'}</td>
                    <td>
                      <ul className="wl-summary-list" style={{ paddingLeft: 18 }}>
                        {l.items.map((it, i) => <li key={i}>{it}</li>)}
                      </ul>
                    </td>
                    <td>{l.hours ? `${l.hours}h` : '—'}</td>
                    <td>{typeof l.progress === 'number' ? `${l.progress}%` : '—'}</td>
                    <td><button className="wl-btn wl-btn-sm wl-btn-danger" onClick={() => handleLogDelete(l.id)}>삭제</button></td>
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

export default ProjectDetail;
