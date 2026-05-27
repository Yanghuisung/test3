import { useEffect, useMemo, useState, type ReactElement } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { listProjects, listLogs, listReportSummariesForPeriod, saveReportSummary, deleteReportSummary, type ReportSummary } from '../utils/db';
import {
  toIsoDate,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  latestProgress,
} from '../utils/storage';
import { generateReportSummary } from '../utils/openai';
import { useToast } from '../contexts/ToastContext';
import type { Project, WorkLog } from '../types';

type Range = 'weekly' | 'monthly';

const WorkLogReport = (): ReactElement => {
  const { showToast } = useToast();
  const [params, setParams] = useSearchParams();

  const [projects, setProjects] = useState<Project[]>([]);
  const [logs, setLogs] = useState<WorkLog[]>([]);
  const [summaries, setSummaries] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingKey, setGeneratingKey] = useState<string | null>(null);

  const range = (params.get('range') as Range) || 'weekly';
  const anchor = params.get('date') || toIsoDate(new Date());
  const projectId = params.get('projectId') || '';

  const handleProjectChange = (id: string) => {
    const next = new URLSearchParams({ range, date: anchor });
    if (id) next.set('projectId', id);
    setParams(next, { replace: true });
  };

  const { startDate, endDate } = useMemo(() => {
    if (range === 'weekly') return { startDate: startOfWeek(anchor), endDate: endOfWeek(anchor) };
    return { startDate: startOfMonth(anchor), endDate: endOfMonth(anchor) };
  }, [range, anchor]);

  useEffect(() => {
    const load = async () => {
      const [p, l, s] = await Promise.all([
        listProjects(),
        listLogs(),
        listReportSummariesForPeriod(range, startDate, endDate),
      ]);
      setProjects(p);
      setLogs(l);
      setSummaries(s);
      setLoading(false);
    };
    load().catch((err) => {
      console.error(err);
      showToast('데이터를 불러오는 중 오류가 발생했습니다.', 'error');
      setLoading(false);
    });
  }, [range, startDate, endDate]);

  const targetProjects = useMemo(
    () => (projectId ? projects.filter((p) => p.id === projectId) : projects),
    [projects, projectId]
  );

  const rangeLabel = range === 'weekly' ? '주간' : '월간';
  const today = toIsoDate(new Date());

  const getSummary = (key: string) => summaries.find((s) => s.projectKey === key);

  const handleGenerate = async (projectKey: string, projectName: string, items: string[]) => {
    setGeneratingKey(projectKey);
    try {
      const content = await generateReportSummary(rangeLabel, startDate, endDate, projectName, items);
      const saved = await saveReportSummary(projectKey, range, startDate, endDate, content);
      setSummaries((prev) => {
        const filtered = prev.filter((s) => s.projectKey !== projectKey);
        return [...filtered, saved];
      });
      showToast('AI 요약이 생성되었습니다.', 'success');
    } catch (err) {
      console.error(err);
      showToast(err instanceof Error ? err.message : 'AI 요약 생성 중 오류가 발생했습니다.', 'error');
    } finally {
      setGeneratingKey(null);
    }
  };

  const handleDelete = async (projectKey: string) => {
    const existing = getSummary(projectKey);
    if (!existing) return;
    try {
      await deleteReportSummary(existing.id);
      setSummaries((prev) => prev.filter((s) => s.projectKey !== projectKey));
      showToast('AI 요약이 삭제되었습니다.', 'success');
    } catch (err) {
      console.error(err);
      showToast('AI 요약 삭제 중 오류가 발생했습니다.', 'error');
    }
  };

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
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            className="rpt-project-select"
            value={projectId}
            onChange={(e) => handleProjectChange(e.target.value)}
          >
            <option value="">전체 프로젝트</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
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
              {projectId && (
                <span>프로젝트 : {projects.find((p) => p.id === projectId)?.name ?? ''}</span>
              )}
              <span>보고 기간 : {startDate} ~ {endDate}</span>
              <span>작 성 일 &nbsp;: {today}</span>
            </div>
          </div>

          {/* 결재란 */}
          <table className="rpt-approval">
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
            const inRange = pLogs.filter((l) => l.date >= startDate && l.date <= endDate);
            const prog = latestProgress(pLogs);

            const allItems = Array.from(
              new Set(inRange.flatMap((l) => l.items.map((it) => it.trim())).filter(Boolean))
            );

            if (allItems.length === 0) return null;

            const existing = getSummary(p.id);
            const isGenerating = generatingKey === p.id;

            return (
              <div className="rpt-project" key={p.id}>
                <div className="rpt-project-header">
                  <span className="rpt-project-name">{p.name}</span>
                  <span className="rpt-project-badge">진척률 {prog}%</span>
                </div>
                <div className="rpt-progress-bar">
                  <div className="rpt-progress-fill" style={{ width: `${prog}%` }} />
                </div>

                {/* AI 요약 또는 원본 항목 */}
                {existing ? (
                  <div className="rpt-ai-content">
                    {existing.content.split('\n').filter(Boolean).map((line, i) => (
                      <p key={i} className="rpt-ai-line">{line}</p>
                    ))}
                  </div>
                ) : (
                  <ul className="rpt-item-list">
                    {allItems.map((it, i) => <li key={i}>{it}</li>)}
                  </ul>
                )}

                {/* Screen-only AI controls */}
                <div className="rpt-ai-controls">
                  {existing ? (
                    <>
                      <button
                        className="rpt-ai-btn rpt-ai-btn-regen"
                        disabled={isGenerating}
                        onClick={() => handleGenerate(p.id, p.name, allItems)}
                      >
                        {isGenerating ? '생성 중…' : '↺ 재생성'}
                      </button>
                      <button
                        className="rpt-ai-btn rpt-ai-btn-del"
                        disabled={isGenerating}
                        onClick={() => handleDelete(p.id)}
                      >
                        원본으로 복원
                      </button>
                    </>
                  ) : (
                    <button
                      className="rpt-ai-btn rpt-ai-btn-gen"
                      disabled={isGenerating}
                      onClick={() => handleGenerate(p.id, p.name, allItems)}
                    >
                      {isGenerating ? '생성 중…' : '✦ AI 요약 생성'}
                    </button>
                  )}
                </div>
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
