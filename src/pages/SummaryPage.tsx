import { useEffect, useMemo, useState, type ReactElement } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { listProjects, listMembers, listLogs } from '../utils/db';
import {
  summarize,
  toIsoDate,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  latestProgress,
} from '../utils/storage';
import type { Project, Member, WorkLog } from '../types';

type Range = 'daily' | 'weekly' | 'monthly';

const SummaryPage = (): ReactElement => {
  const [params, setParams] = useSearchParams();
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);

  const initialProjectId = params.get('projectId') ?? '';
  const initialRange = (params.get('range') as Range) || 'weekly';
  const initialAnchor = params.get('date') || toIsoDate(new Date());

  const [projectId, setProjectId] = useState(initialProjectId);
  const [range, setRange] = useState<Range>(initialRange);
  const [anchor, setAnchor] = useState(initialAnchor);

  useEffect(() => {
    const load = async () => {
      const [p, m, l] = await Promise.all([listProjects(), listMembers(), listLogs()]);
      setProjects(p);
      setMembers(m);
      setLogs(l);
    };
    load().catch(console.error);
  }, []);

  useEffect(() => {
    const next: Record<string, string> = { range, date: anchor };
    if (projectId) next.projectId = projectId;
    setParams(next, { replace: true });
  }, [projectId, range, anchor, setParams]);

  const { startDate, endDate } = useMemo(() => {
    if (range === 'daily') return { startDate: anchor, endDate: anchor };
    if (range === 'weekly') return { startDate: startOfWeek(anchor), endDate: endOfWeek(anchor) };
    return { startDate: startOfMonth(anchor), endDate: endOfMonth(anchor) };
  }, [range, anchor]);

  const targetProjects = useMemo(
    () => (projectId ? projects.filter((p) => p.id === projectId) : projects),
    [projects, projectId]
  );

  const rangeLabel = range === 'daily' ? '일간' : range === 'weekly' ? '주간' : '월간';

  const handleCopy = () => {
    const lines: string[] = [];
    lines.push(`【${rangeLabel} 업무 요약】 ${startDate} ~ ${endDate}`);
    lines.push('');
    for (const p of targetProjects) {
      const pLogs = logs.filter((l) => l.projectId === p.id);
      const groups = summarize(pLogs, startDate, endDate, members);
      if (groups.length === 0) continue;
      lines.push(`■ ${p.name} (진척률 ${latestProgress(pLogs)}%)`);
      for (const g of groups) {
        lines.push(`  ▸ ${g.memberName}`);
        for (const item of g.items) lines.push(`    - ${item}`);
      }
      lines.push('');
    }
    const text = lines.join('\n');
    navigator.clipboard?.writeText(text).then(
      () => alert('요약을 클립보드에 복사했습니다.'),
      () => alert('복사 실패 — 브라우저 권한을 확인하세요.')
    );
  };

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">{rangeLabel} 요약</h1>
          <p className="wl-page-sub">{startDate} ~ {endDate} · 개조식 자동 집계</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="wl-btn" onClick={handleCopy}>전체 복사</button>
          <button className="wl-btn" onClick={() => window.print()}>인쇄</button>
        </div>
      </div>

      <div className="wl-section">
        <div className="wl-field-row">
          <div className="wl-field">
            <label>구간</label>
            <select value={range} onChange={(e) => setRange(e.target.value as Range)}>
              <option value="daily">일간</option>
              <option value="weekly">주간</option>
              <option value="monthly">월간</option>
            </select>
          </div>
          <div className="wl-field">
            <label>기준일</label>
            <input type="date" value={anchor} onChange={(e) => setAnchor(e.target.value)} />
          </div>
          <div className="wl-field">
            <label>프로젝트</label>
            <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
              <option value="">전체</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
        </div>
      </div>

      {targetProjects.length === 0 ? (
        <div className="wl-section wl-empty">
          <h3>표시할 프로젝트가 없습니다</h3>
          <Link to="/projects/new" className="wl-btn wl-btn-primary">새 프로젝트</Link>
        </div>
      ) : (
        targetProjects.map((p) => {
          const pLogs = logs.filter((l) => l.projectId === p.id);
          const groups = summarize(pLogs, startDate, endDate, members);
          const prog = latestProgress(pLogs);
          return (
            <div className="wl-section" key={p.id}>
              <div className="wl-section-head">
                <h2 className="wl-section-title">
                  <Link to={`/projects/${p.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                    {p.name}
                  </Link>
                </h2>
                <span className="wl-trend-progress">현재 진척률 {prog}%</span>
              </div>
              {groups.length === 0 ? (
                <p className="wl-kpi-hint" style={{ margin: 0 }}>해당 구간에 작성된 일지가 없습니다.</p>
              ) : (
                groups.map((g) => (
                  <div className="wl-summary-card" key={g.memberId}>
                    <div className="wl-summary-member">{g.memberName}</div>
                    <ul className="wl-summary-list">
                      {g.items.map((it, i) => <li key={i}>{it}</li>)}
                    </ul>
                  </div>
                ))
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default SummaryPage;
