import type { Project, Member, WorkLog } from '../types';

/* ── Date utilities ───────────────────────── */

export const toIsoDate = (d: Date): string => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export const startOfWeek = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return toIsoDate(d);
};

export const endOfWeek = (iso: string): string => {
  const start = new Date(startOfWeek(iso) + 'T00:00:00');
  start.setDate(start.getDate() + 6);
  return toIsoDate(start);
};

export const startOfMonth = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  d.setDate(1);
  return toIsoDate(d);
};

export const endOfMonth = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  d.setMonth(d.getMonth() + 1);
  d.setDate(0);
  return toIsoDate(d);
};

export const daysBetween = (a: string, b: string): number => {
  const ad = new Date(a + 'T00:00:00').getTime();
  const bd = new Date(b + 'T00:00:00').getTime();
  return Math.round((bd - ad) / 86400000);
};

/* ── Pure aggregations (take pre-fetched data as params) ── */

export interface ProgressPoint {
  date: string;
  progress: number;
}

export const progressSeries = (logs: WorkLog[]): ProgressPoint[] => {
  const filtered = logs.filter((l) => typeof l.progress === 'number');
  const byDate = new Map<string, number>();
  for (const l of filtered) {
    const cur = byDate.get(l.date) ?? 0;
    byDate.set(l.date, Math.max(cur, l.progress!));
  }
  const arr = Array.from(byDate.entries())
    .map(([date, progress]) => ({ date, progress }))
    .sort((a, b) => a.date.localeCompare(b.date));
  // 단조 증가 보정
  let max = 0;
  return arr.map((p) => {
    max = Math.max(max, p.progress);
    return { date: p.date, progress: max };
  });
};

export const latestProgress = (logs: WorkLog[]): number => {
  const series = progressSeries(logs);
  return series.length ? series[series.length - 1].progress : 0;
};

export const lastLogDate = (logs: WorkLog[]): string | null => {
  const sorted = [...logs].sort((a, b) => a.date.localeCompare(b.date));
  return sorted.length ? sorted[sorted.length - 1].date : null;
};

export interface SummaryGroup {
  memberId: string;
  memberName: string;
  items: string[];
}

export const summarize = (
  logs: WorkLog[],
  startDate: string,
  endDate: string,
  members: Member[]
): SummaryGroup[] => {
  const inRange = logs.filter((l) => l.date >= startDate && l.date <= endDate);
  const byMember = new Map<string, Set<string>>();
  for (const l of inRange) {
    if (!byMember.has(l.memberId)) byMember.set(l.memberId, new Set());
    for (const item of l.items) {
      const trimmed = item.trim();
      if (trimmed) byMember.get(l.memberId)!.add(trimmed);
    }
  }
  const groups: SummaryGroup[] = [];
  for (const [memberId, set] of byMember) {
    const m = members.find((x) => x.id === memberId);
    groups.push({
      memberId,
      memberName: m?.name ?? '(알 수 없음)',
      items: Array.from(set),
    });
  }
  return groups.sort((a, b) => a.memberName.localeCompare(b.memberName));
};

export interface DashboardKpi {
  totalProjects: number;
  activeProjects: number;
  completedProjects: number;
  totalMembers: number;
  todayLogs: number;
  weekLogs: number;
}

export const dashboardKpi = (
  projects: Project[],
  logs: WorkLog[],
  members: Member[],
  today: string
): DashboardKpi => {
  const wkStart = startOfWeek(today);
  const wkEnd = endOfWeek(today);
  return {
    totalProjects: projects.length,
    activeProjects: projects.filter((p) => p.status === 'active').length,
    completedProjects: projects.filter((p) => p.status === 'completed').length,
    totalMembers: members.length,
    todayLogs: logs.filter((l) => l.date === today).length,
    weekLogs: logs.filter((l) => l.date >= wkStart && l.date <= wkEnd).length,
  };
};

export interface DelayedProject {
  project: Project;
  daysSinceLog: number;
  daysSinceProgress: number;
  progress: number;
  reason: string;
}

export const delayedProjects = (
  projects: Project[],
  logs: WorkLog[],
  staleDays = 7,
  today: string = toIsoDate(new Date())
): DelayedProject[] => {
  const out: DelayedProject[] = [];
  for (const p of projects) {
    if (p.status !== 'active') continue;
    const pLogs = logs.filter((l) => l.projectId === p.id);
    const last = lastLogDate(pLogs);
    const series = progressSeries(pLogs);
    const lastProgDate = series.length ? series[series.length - 1].date : null;
    const dSinceLog = last ? daysBetween(last, today) : 999;
    const dSinceProg = lastProgDate ? daysBetween(lastProgDate, today) : 999;
    const progress = latestProgress(pLogs);
    const reasons: string[] = [];
    if (dSinceLog >= staleDays) reasons.push(last ? `${dSinceLog}일 무로그` : '로그 없음');
    if (dSinceProg >= staleDays && progress < 100) {
      reasons.push(lastProgDate ? `${dSinceProg}일 진척 정체` : '진척률 미입력');
    }
    if (reasons.length > 0) {
      out.push({
        project: p,
        daysSinceLog: dSinceLog,
        daysSinceProgress: dSinceProg,
        progress,
        reason: reasons.join(' · '),
      });
    }
  }
  return out.sort((a, b) => b.daysSinceLog - a.daysSinceLog);
};
