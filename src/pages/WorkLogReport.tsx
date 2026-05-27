import { useEffect, useMemo, useState, type ReactElement, type ChangeEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { listProjects, listMembers, listLogs } from '../utils/db';
import {
  summarize,
  memberHoursSummary,
  toIsoDate,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  latestProgress,
} from '../utils/storage';
import { useToast } from '../contexts/ToastContext';
import type { Project, Member, WorkLog } from '../types';

type Range = 'weekly' | 'monthly';

interface ApprovalNames {
  writer: string;
  reviewer: string;
  approver: string;
}

const WorkLogReport = (): ReactElement => {
  const { showToast } = useToast();
  const [params] = useSearchParams();

  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [names, setNames] = useState<ApprovalNames>({ writer: '', reviewer: '', approver: '' });

  const range = (params.get('range') as Range) || 'weekly';
  const anchor = params.get('date') || toIsoDate(new Date());
  const projectId = params.get('projectId') || '';

  useEffect(() => {
    const load = async () => {
      const [p, m, l] = await Promise.all([listProjects(), listMembers(), listLogs()]);
      setProjects(p);
      setMembers(m);
      setLogs(l);
      setLoading(false);
    };
    load().catch((err) => {
      console.error(err);
      showToast('데이터를 불러오는 중 오류가 발생했습니다.', 'error');
      setLoading(false);
    });
  }, []);

  const { startDate, endDate } = useMemo(() => {
    if (range === 'weekly') return { startDate: startOfWeek(anchor), endDate: endOfWeek(anchor) };
    return { startDate: startOfMonth(anchor), endDate: endOfMonth(anchor) };
  }, [range, anchor]);

  const targetProjects = useMemo(
    () => (projectId ? projects.filter((p) => p.id === projectId) : projects),
    [projects, projectId]
  );

  const rangeLabel = range === 'weekly' ? '주간' : '월간';
  const today = toIsoDate(new Date());

  const setName = (field: keyof ApprovalNames) => (e: ChangeEvent<HTMLInputElement>) =>
    setNames((prev) => ({ ...prev, [field]: e.target.value }));

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <>
      {/* ── Screen-only control bar ── */}
      <div className="rpt-screen-controls">
        <Link to={`/summary?range=${range}&date=${anchor}${projectId ? `&projectId=${projectId}` : ''}`} className="wl-btn">
          ← 요약으로
        </Link>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span className="rpt-screen-hint">결재란에 이름을 입력한 뒤 PDF 저장을 눌러 주세요</span>
          <button className="wl-btn wl-btn-primary" onClick={() => window.print()}>
            PDF 저장 (인쇄)
          </button>
        </div>
      </div>

      {/* ── A4 Report page ── */}
      <div className="rpt-page">

        {/* Header: title + 결재란 */}
        <div className="rpt-header">
          <div className="rpt-title-block">
            <h1 className="rpt-doc-title">{rangeLabel} 업무 보고서</h1>
            <div className="rpt-doc-meta">
              <span>보고 기간 : {startDate} ~ {endDate}</span>
              <span>작 성 일 &nbsp;: {today}</span>
            </div>
          </div>

          {/* 결재란 */}
          <table className="rpt-approval">
            <caption>결 &nbsp; 재 &nbsp; 란</caption>
            <thead>
              <tr>
                <th>작 성</th>
                <th>검 토</th>
                <th>승 인</th>
              </tr>
            </thead>
            <tbody>
              <tr className="rpt-approval-sig">
                <td />
                <td />
                <td />
              </tr>
              <tr className="rpt-approval-name">
                <td>
                  <input
                    className="rpt-name-input"
                    value={names.writer}
                    onChange={setName('writer')}
                    placeholder="이름"
                  />
                </td>
                <td>
                  <input
                    className="rpt-name-input"
                    value={names.reviewer}
                    onChange={setName('reviewer')}
                    placeholder="이름"
                  />
                </td>
                <td>
                  <input
                    className="rpt-name-input"
                    value={names.approver}
                    onChange={setName('approver')}
                    placeholder="이름"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <hr className="rpt-divider" />

        {/* Report body */}
        {targetProjects.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#6b7280', marginTop: 40 }}>
            해당 기간에 표시할 프로젝트가 없습니다.
          </p>
        ) : (
          targetProjects.map((p) => {
            const pLogs = logs.filter((l) => l.projectId === p.id);
            const groups = summarize(pLogs, startDate, endDate, members);
            const hoursData = memberHoursSummary(pLogs, startDate, endDate, members);
            const totalHours = hoursData.reduce((s, h) => s + h.hours, 0);
            const prog = latestProgress(pLogs);

            if (groups.length === 0) return null;

            return (
              <div className="rpt-project" key={p.id}>
                <div className="rpt-project-header">
                  <span className="rpt-project-name">{p.name}</span>
                  <span className="rpt-project-badge">진척률 {prog}%</span>
                </div>
                <div className="rpt-progress-bar">
                  <div className="rpt-progress-fill" style={{ width: `${prog}%` }} />
                </div>

                {groups.map((g) => (
                  <div className="rpt-member-block" key={g.memberId}>
                    <div className="rpt-member-name">▸ {g.memberName}</div>
                    <ul className="rpt-item-list">
                      {g.items.map((it, i) => <li key={i}>{it}</li>)}
                    </ul>
                  </div>
                ))}

                {hoursData.length > 0 && (
                  <div className="rpt-hours-wrap">
                    <div className="rpt-hours-label">투입 공수</div>
                    <table className="rpt-hours-table">
                      <thead>
                        <tr><th>구성원</th><th>공수 (h)</th></tr>
                      </thead>
                      <tbody>
                        {hoursData.map((h) => (
                          <tr key={h.memberId}>
                            <td>{h.memberName}</td>
                            <td>{h.hours}h</td>
                          </tr>
                        ))}
                        <tr className="rpt-hours-total">
                          <td>합계</td>
                          <td>{totalHours}h</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })
        )}

        <div className="rpt-doc-footer">
          본 보고서는 업무일지 관리 시스템에서 자동 생성되었습니다. &nbsp;·&nbsp; 생성일시 {today}
        </div>
      </div>
    </>
  );
};

export default WorkLogReport;
