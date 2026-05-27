import { useEffect, useState, type ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { listProjects, listLogs, listMembers } from '../utils/db';
import {
  dashboardKpi,
  progressSeries,
  latestProgress,
  delayedProjects,
  toIsoDate,
  daysBetween,
  type DashboardKpi,
  type DelayedProject,
  type ProgressPoint,
} from '../utils/storage';
import type { Project, Member, WorkLog } from '../types';

const STALE_DAYS = 7;

const KPI_INIT: DashboardKpi = {
  totalProjects: 0, activeProjects: 0, completedProjects: 0,
  totalMembers: 0, todayLogs: 0, weekLogs: 0,
};

const ProgressMiniChart = ({ data }: { data: ProgressPoint[] }): ReactElement => {
  const W = 320;
  const H = 80;
  const padX = 4;
  if (data.length === 0) {
    return (
      <svg className="wl-trend-svg" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        <text x="50%" y="50%" textAnchor="middle" fontSize="11" fill="#9ca3af" dominantBaseline="middle">
          진척률 데이터 없음
        </text>
      </svg>
    );
  }
  const xs = data.map((_, i) => padX + (i * (W - 2 * padX)) / Math.max(1, data.length - 1));
  const ys = data.map((p) => H - 6 - (p.progress / 100) * (H - 12));
  const pathD = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${ys[i].toFixed(1)}`).join(' ');
  const areaD = `${pathD} L ${xs[xs.length - 1].toFixed(1)} ${H - 6} L ${xs[0].toFixed(1)} ${H - 6} Z`;
  return (
    <svg className="wl-trend-svg" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      <line x1="0" y1={H - 6} x2={W} y2={H - 6} stroke="currentColor" strokeOpacity="0.15" />
      <path d={areaD} fill="currentColor" fillOpacity="0.12" />
      <path d={pathD} fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {xs.map((x, i) => (
        <circle key={i} cx={x} cy={ys[i]} r="2.5" fill="currentColor" />
      ))}
    </svg>
  );
};

const Dashboard = (): ReactElement => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);
  const [kpi, setKpi] = useState<DashboardKpi>(KPI_INIT);
  const [delayed, setDelayed] = useState<DelayedProject[]>([]);

  const today = toIsoDate(new Date());

  useEffect(() => {
    const load = async () => {
      const [p, m, l] = await Promise.all([listProjects(), listMembers(), listLogs()]);
      setProjects(p);
      setMembers(m);
      setLogs(l);
      setKpi(dashboardKpi(p, l, m, today));
      setDelayed(delayedProjects(p, l, STALE_DAYS, today));
    };
    load().catch(console.error);
  }, []);

  const activeProjects = projects.filter((p) => p.status === 'active');

  const recentLogs = [...logs]
    .sort((a, b) => b.date.localeCompare(a.date) || b.updatedAt.localeCompare(a.updatedAt))
    .slice(0, 6);

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">관리자 대시보드</h1>
          <p className="wl-page-sub">오늘 {today} · 프로젝트 진행 현황 한눈에 보기</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/logs/new" className="wl-btn wl-btn-primary">+ 일지 작성</Link>
          <Link to="/projects/new" className="wl-btn">새 프로젝트</Link>
        </div>
      </div>

      <div className="wl-kpi-grid">
        <div className="wl-kpi">
          <span className="wl-kpi-label">전체 프로젝트</span>
          <div className="wl-kpi-value">{kpi.totalProjects}</div>
          <span className="wl-kpi-hint">진행 {kpi.activeProjects} · 완료 {kpi.completedProjects}</span>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">구성원</span>
          <div className="wl-kpi-value">{kpi.totalMembers}</div>
          <span className="wl-kpi-hint">투입 인력 총원</span>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">오늘 작성된 일지</span>
          <div className="wl-kpi-value">{kpi.todayLogs}</div>
          <span className="wl-kpi-hint">금일 등록 건수</span>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">이번 주 일지</span>
          <div className="wl-kpi-value">{kpi.weekLogs}</div>
          <span className="wl-kpi-hint">월–일 누적</span>
        </div>
        <div className="wl-kpi">
          <span className="wl-kpi-label">지연 프로젝트</span>
          <div className="wl-kpi-value" style={{ color: delayed.length ? '#C8102E' : undefined }}>
            {delayed.length}
          </div>
          <span className="wl-kpi-hint">{STALE_DAYS}일+ 무로그 또는 정체</span>
        </div>
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">프로젝트별 진행 트렌드</h2>
          <Link to="/projects" className="wl-btn wl-btn-sm">전체 보기</Link>
        </div>
        {activeProjects.length === 0 ? (
          <div className="wl-empty">
            <h3>활성 프로젝트가 없습니다</h3>
            <p>새 프로젝트를 만들어 진행 상황을 추적해 보세요.</p>
            <Link to="/projects/new" className="wl-btn wl-btn-primary">+ 프로젝트 추가</Link>
          </div>
        ) : (
          <div className="wl-trend-grid">
            {activeProjects.map((p) => {
              const pLogs = logs.filter((l) => l.projectId === p.id);
              const series = progressSeries(pLogs);
              const prog = latestProgress(pLogs);
              return (
                <div className="wl-trend-card" key={p.id}>
                  <div className="wl-trend-head">
                    <Link className="wl-trend-title" to={`/projects/${p.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                      {p.name}
                    </Link>
                    <span className="wl-trend-progress">진척률 {prog}%</span>
                  </div>
                  <ProgressMiniChart data={series} />
                  <div className="wl-progress" style={{ marginTop: 8 }}>
                    <div className="wl-progress-fill" style={{ width: `${prog}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">진행 지연 프로젝트</h2>
          <span className="wl-kpi-hint">{STALE_DAYS}일 이상 무로그 또는 진척 정체</span>
        </div>
        {delayed.length === 0 ? (
          <div className="wl-empty">
            <p style={{ margin: 0 }}>지연 중인 프로젝트가 없습니다. 잘 굴러가고 있어요.</p>
          </div>
        ) : (
          <div>
            {delayed.map((d) => (
              <div className="wl-delayed-row" key={d.project.id}>
                <div className="wl-delayed-name">
                  <Link to={`/projects/${d.project.id}`}>{d.project.name}</Link>
                  <div className="wl-delayed-reason">{d.reason}</div>
                </div>
                <span className="wl-badge wl-badge-warn">진척 {d.progress}%</span>
                <span className="wl-kpi-hint">
                  최종 로그 {d.daysSinceLog >= 999 ? '없음' : `${d.daysSinceLog}일 전`}
                </span>
                <Link to="/logs/new" className="wl-btn wl-btn-sm">일지 작성</Link>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="wl-section">
        <div className="wl-section-head">
          <h2 className="wl-section-title">최근 일지</h2>
          <Link to="/summary" className="wl-btn wl-btn-sm">요약 보기</Link>
        </div>
        {recentLogs.length === 0 ? (
          <div className="wl-empty"><p style={{ margin: 0 }}>작성된 일지가 없습니다.</p></div>
        ) : (
          <table className="wl-table">
            <thead>
              <tr>
                <th>일자</th>
                <th>프로젝트</th>
                <th>작성자</th>
                <th>항목 수</th>
                <th>공수</th>
                <th>진척률</th>
              </tr>
            </thead>
            <tbody>
              {recentLogs.map((l) => {
                const p = projects.find((x) => x.id === l.projectId);
                const m = members.find((x) => x.id === l.memberId);
                return (
                  <tr key={l.id}>
                    <td>{l.date}</td>
                    <td>{p ? <Link to={`/projects/${p.id}`}>{p.name}</Link> : '—'}</td>
                    <td>{m?.name ?? '—'}</td>
                    <td>{l.items.length}</td>
                    <td>{l.hours ? `${l.hours}h` : '—'}</td>
                    <td>{typeof l.progress === 'number' ? `${l.progress}%` : '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="wl-kpi-hint" style={{ textAlign: 'center', marginTop: 24 }}>
        오늘로부터 마지막 일지까지 {recentLogs[0] ? `${daysBetween(recentLogs[0].date, today)}일` : '-'} 경과
      </div>
    </div>
  );
};

export default Dashboard;
