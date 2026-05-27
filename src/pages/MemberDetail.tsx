import { useEffect, useState, useCallback, type ReactElement } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getMember, logsByMember, listProjects, deleteLog } from '../utils/db';
import { useCurrentUser } from '../contexts/CurrentUserContext';
import type { Member, WorkLog, Project } from '../types';

const MemberDetail = (): ReactElement => {
  const { id } = useParams<{ id: string }>();
  const { currentMemberId } = useCurrentUser();

  const [member, setMember] = useState<Member | undefined>();
  const [logs, setLogs] = useState<WorkLog[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [notFound, setNotFound] = useState(false);

  const refresh = useCallback(async () => {
    const [m, l, p] = await Promise.all([getMember(id!), logsByMember(id!), listProjects()]);
    if (!m) { setNotFound(true); return; }
    setMember(m);
    setLogs(l);
    setProjects(p);
  }, [id]);

  useEffect(() => { refresh().catch(console.error); }, [refresh]);

  if (notFound) return (
    <div className="wl-container">
      <div className="wl-empty">
        <h3>구성원을 찾을 수 없습니다</h3>
        <Link to="/members" className="wl-btn">목록으로</Link>
      </div>
    </div>
  );

  if (!member) return <div className="wl-container"><div className="wl-empty">불러오는 중…</div></div>;

  const isOwner = currentMemberId === member.id;
  const totalHours = logs.reduce((s, l) => s + (l.hours ?? 0), 0);

  const handleLogDelete = (log: WorkLog) => {
    if (!confirm('이 일지를 삭제할까요?')) return;
    deleteLog(log.id).then(() => refresh()).catch(console.error);
  };

  const byProject = new Map<string, WorkLog[]>();
  for (const l of logs) {
    if (!byProject.has(l.projectId)) byProject.set(l.projectId, []);
    byProject.get(l.projectId)!.push(l);
  }

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">{member.name}</h1>
          <p className="wl-page-sub">
            {member.role && <span className={`wl-badge ${member.role === 'PM' ? 'wl-badge-pm' : 'wl-badge-active'}`}>{member.role}</span>}
            {member.email && <span style={{ marginLeft: 10 }}>{member.email}</span>}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/members" className="wl-btn">목록으로</Link>
        </div>
      </div>

      <div className="wl-kpi-grid">
        <div className="wl-kpi">
          <span className="wl-kpi-label">전체 일지</span>
          <div className="wl-kpi-value">{logs.length}</div>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">투입 공수 합계</span>
          <div className="wl-kpi-value">{totalHours}h</div>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">참여 프로젝트</span>
          <div className="wl-kpi-value">{byProject.size}</div>
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="wl-section wl-empty">
          <p style={{ margin: 0 }}>작성된 일지가 없습니다.</p>
        </div>
      ) : (
        Array.from(byProject.entries()).map(([projectId, pLogs]) => {
          const project = projects.find((p) => p.id === projectId);
          return (
            <div className="wl-section" key={projectId}>
              <div className="wl-section-head">
                <h2 className="wl-section-title">
                  {project ? (
                    <Link to={`/projects/${projectId}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                      {project.name}
                    </Link>
                  ) : '(삭제된 프로젝트)'}
                </h2>
                <span className="wl-trend-progress">{pLogs.length}건 · {pLogs.reduce((s, l) => s + (l.hours ?? 0), 0)}h</span>
              </div>
              <table className="wl-table">
                <thead>
                  <tr><th>일자</th><th>항목</th><th>공수</th><th>진척</th><th></th></tr>
                </thead>
                <tbody>
                  {pLogs.map((l) => (
                    <tr key={l.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>{l.date}</td>
                      <td>
                        <ul className="wl-summary-list" style={{ paddingLeft: 18 }}>
                          {l.items.map((it, i) => <li key={i}>{it}</li>)}
                        </ul>
                      </td>
                      <td>{l.hours ? `${l.hours}h` : '—'}</td>
                      <td>{typeof l.progress === 'number' ? `${l.progress}%` : '—'}</td>
                      <td style={{ whiteSpace: 'nowrap' }}>
                        {isOwner ? (
                          <>
                            <Link to={`/logs/${l.id}/edit`} className="wl-btn wl-btn-sm" style={{ marginRight: 6 }}>수정</Link>
                            <button className="wl-btn wl-btn-sm wl-btn-danger" onClick={() => handleLogDelete(l)}>삭제</button>
                          </>
                        ) : (
                          <span className="wl-kpi-hint">열람만 가능</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })
      )}

      {isOwner && (
        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <Link to="/logs/new" className="wl-btn wl-btn-primary">+ 일지 작성</Link>
        </div>
      )}
    </div>
  );
};

export default MemberDetail;
