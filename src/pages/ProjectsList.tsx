import { useEffect, useState, type ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { listProjects, listMembers, listLogs } from '../utils/db';
import { latestProgress, lastLogDate, toIsoDate, daysBetween } from '../utils/storage';
import type { Project, Member, WorkLog } from '../types';

const statusLabel: Record<Project['status'], string> = {
  active: '진행',
  paused: '보류',
  completed: '완료',
};

const ProjectsList = (): ReactElement => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);

  useEffect(() => {
    const load = async () => {
      const [p, m, l] = await Promise.all([listProjects(), listMembers(), listLogs()]);
      setProjects(p);
      setMembers(m);
      setLogs(l);
    };
    load().catch(console.error);
  }, []);

  const today = toIsoDate(new Date());

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">프로젝트</h1>
          <p className="wl-page-sub">전체 프로젝트 목록과 현재 진척률</p>
        </div>
        <Link to="/projects/new" className="wl-btn wl-btn-primary">+ 새 프로젝트</Link>
      </div>

      <div className="wl-section">
        {projects.length === 0 ? (
          <div className="wl-empty">
            <h3>등록된 프로젝트가 없습니다</h3>
            <Link to="/projects/new" className="wl-btn wl-btn-primary">첫 프로젝트 만들기</Link>
          </div>
        ) : (
          <table className="wl-table">
            <thead>
              <tr>
                <th>이름</th>
                <th>상태</th>
                <th>구성원</th>
                <th>시작</th>
                <th>최근 로그</th>
                <th>진척률</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => {
                const pLogs = logs.filter((l) => l.projectId === p.id);
                const prog = latestProgress(pLogs);
                const last = lastLogDate(pLogs);
                const ageDays = last ? daysBetween(last, today) : null;
                return (
                  <tr key={p.id}>
                    <td>
                      <Link to={`/projects/${p.id}`} style={{ fontWeight: 500, color: 'inherit' }}>
                        {p.name}
                      </Link>
                      {p.description && (
                        <div className="wl-kpi-hint" style={{ marginTop: 2 }}>{p.description}</div>
                      )}
                    </td>
                    <td>
                      <span className={`wl-badge wl-badge-${p.status}`}>{statusLabel[p.status]}</span>
                    </td>
                    <td>
                      <div className="wl-chip-list">
                        {p.memberIds.map((mid) => {
                          const m = members.find((x) => x.id === mid);
                          return m ? <span key={mid} className="wl-chip">{m.name}</span> : null;
                        })}
                        {p.memberIds.length === 0 && <span className="wl-kpi-hint">미배정</span>}
                      </div>
                    </td>
                    <td>{p.startDate}</td>
                    <td>{last ? `${last} (${ageDays}일 전)` : <span className="wl-kpi-hint">없음</span>}</td>
                    <td style={{ minWidth: 140 }}>
                      <div className="wl-progress" style={{ marginBottom: 4 }}>
                        <div className="wl-progress-fill" style={{ width: `${prog}%` }} />
                      </div>
                      <span className="wl-kpi-hint">{prog}%</span>
                    </td>
                    <td>
                      <Link to={`/projects/${p.id}/edit`} className="wl-btn wl-btn-sm">수정</Link>
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

export default ProjectsList;
