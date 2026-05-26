import type { Project, Member, WorkLog } from '../types';

const K_PROJECTS = 'worklog.projects';
const K_MEMBERS  = 'worklog.members';
const K_LOGS     = 'worklog.logs';

const readArr = <T,>(key: string): T[] => {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    const v = JSON.parse(raw);
    return Array.isArray(v) ? (v as T[]) : [];
  } catch {
    return [];
  }
};

const writeArr = <T,>(key: string, list: T[]): void => {
  localStorage.setItem(key, JSON.stringify(list));
};

const newId = (): string =>
  Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

const nowIso = (): string => new Date().toISOString();

/* ── Projects ─────────────────────────────── */

export const listProjects = (): Project[] => readArr<Project>(K_PROJECTS);

export const getProject = (id: string): Project | undefined =>
  listProjects().find((p) => p.id === id);

export const saveProject = (
  input: Omit<Project, 'id' | 'createdAt'> & { id?: string }
): Project => {
  const list = listProjects();
  if (input.id) {
    const idx = list.findIndex((p) => p.id === input.id);
    if (idx >= 0) {
      const updated: Project = { ...list[idx], ...input, id: input.id };
      list[idx] = updated;
      writeArr(K_PROJECTS, list);
      return updated;
    }
  }
  const created: Project = {
    id: newId(),
    createdAt: nowIso(),
    ...input,
  };
  list.push(created);
  writeArr(K_PROJECTS, list);
  return created;
};

export const deleteProject = (id: string): void => {
  writeArr(K_PROJECTS, listProjects().filter((p) => p.id !== id));
  writeArr(K_LOGS, listLogs().filter((l) => l.projectId !== id));
};

/* ── Members ──────────────────────────────── */

export const listMembers = (): Member[] => readArr<Member>(K_MEMBERS);

export const getMember = (id: string): Member | undefined =>
  listMembers().find((m) => m.id === id);

export const saveMember = (
  input: Omit<Member, 'id' | 'createdAt'> & { id?: string }
): Member => {
  const list = listMembers();
  if (input.id) {
    const idx = list.findIndex((m) => m.id === input.id);
    if (idx >= 0) {
      const updated: Member = { ...list[idx], ...input, id: input.id };
      list[idx] = updated;
      writeArr(K_MEMBERS, list);
      return updated;
    }
  }
  const created: Member = { id: newId(), createdAt: nowIso(), ...input };
  list.push(created);
  writeArr(K_MEMBERS, list);
  return created;
};

export const deleteMember = (id: string): void => {
  writeArr(K_MEMBERS, listMembers().filter((m) => m.id !== id));
  const projects = listProjects().map((p) => ({
    ...p,
    memberIds: p.memberIds.filter((mid) => mid !== id),
  }));
  writeArr(K_PROJECTS, projects);
};

/* ── WorkLogs ─────────────────────────────── */

export const listLogs = (): WorkLog[] => readArr<WorkLog>(K_LOGS);

export const getLog = (id: string): WorkLog | undefined =>
  listLogs().find((l) => l.id === id);

export const saveLog = (
  input: Omit<WorkLog, 'id' | 'createdAt' | 'updatedAt'> & { id?: string }
): WorkLog => {
  const list = listLogs();
  const now = nowIso();
  if (input.id) {
    const idx = list.findIndex((l) => l.id === input.id);
    if (idx >= 0) {
      const updated: WorkLog = { ...list[idx], ...input, id: input.id, updatedAt: now };
      list[idx] = updated;
      writeArr(K_LOGS, list);
      return updated;
    }
  }
  const created: WorkLog = {
    id: newId(),
    createdAt: now,
    updatedAt: now,
    ...input,
  };
  list.push(created);
  writeArr(K_LOGS, list);
  return created;
};

export const deleteLog = (id: string): void => {
  writeArr(K_LOGS, listLogs().filter((l) => l.id !== id));
};

/* ── Query helpers ────────────────────────── */

export const logsByProject = (projectId: string): WorkLog[] =>
  listLogs()
    .filter((l) => l.projectId === projectId)
    .sort((a, b) => a.date.localeCompare(b.date));

export const logsInRange = (
  projectId: string,
  startDate: string,
  endDate: string
): WorkLog[] =>
  logsByProject(projectId).filter(
    (l) => l.date >= startDate && l.date <= endDate
  );

/* ── Date utilities ───────────────────────── */

export const toIsoDate = (d: Date): string => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export const startOfWeek = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  const day = d.getDay(); // 0=Sun
  const diff = day === 0 ? -6 : 1 - day; // Mon-start
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

/* ── Aggregations ─────────────────────────── */

export interface ProgressPoint {
  date: string;
  progress: number;
}

/** 프로젝트 progress 시계열 — 일별 최대 progress 값 사용 */
export const progressSeries = (projectId: string): ProgressPoint[] => {
  const logs = logsByProject(projectId).filter((l) => typeof l.progress === 'number');
  const byDate = new Map<string, number>();
  for (const l of logs) {
    const cur = byDate.get(l.date) ?? 0;
    byDate.set(l.date, Math.max(cur, l.progress!));
  }
  const arr = Array.from(byDate.entries())
    .map(([date, progress]) => ({ date, progress }))
    .sort((a, b) => a.date.localeCompare(b.date));
  // 단조 증가 보정 (한 번 진척된 건 떨어지지 않음)
  let max = 0;
  return arr.map((p) => {
    max = Math.max(max, p.progress);
    return { date: p.date, progress: max };
  });
};

export const latestProgress = (projectId: string): number => {
  const series = progressSeries(projectId);
  return series.length ? series[series.length - 1].progress : 0;
};

export const lastLogDate = (projectId: string): string | null => {
  const logs = logsByProject(projectId);
  return logs.length ? logs[logs.length - 1].date : null;
};

/** 지연 프로젝트 판정: 활성 상태 + (최근 N일 무로그) 또는 (progress 정체 N일) */
export interface DelayedProject {
  project: Project;
  daysSinceLog: number;
  daysSinceProgress: number;
  progress: number;
  reason: string;
}

export const delayedProjects = (
  staleDays = 7,
  today: string = toIsoDate(new Date())
): DelayedProject[] => {
  const out: DelayedProject[] = [];
  for (const p of listProjects()) {
    if (p.status !== 'active') continue;
    const last = lastLogDate(p.id);
    const series = progressSeries(p.id);
    const lastProgDate = series.length ? series[series.length - 1].date : null;
    const dSinceLog = last ? daysBetween(last, today) : 999;
    const dSinceProg = lastProgDate ? daysBetween(lastProgDate, today) : 999;
    const progress = latestProgress(p.id);
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

/** 일/주/월 단위 항목 머지 (중복 제거, 멤버별 그룹) */
export interface SummaryGroup {
  memberId: string;
  memberName: string;
  items: string[];
}

export const summarize = (
  projectId: string,
  startDate: string,
  endDate: string,
  members: Member[]
): SummaryGroup[] => {
  const logs = logsInRange(projectId, startDate, endDate);
  const byMember = new Map<string, Set<string>>();
  for (const l of logs) {
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

/* ── Counts for dashboard KPIs ───────────── */

export interface DashboardKpi {
  totalProjects: number;
  activeProjects: number;
  completedProjects: number;
  totalMembers: number;
  todayLogs: number;
  weekLogs: number;
}

export const dashboardKpi = (today: string = toIsoDate(new Date())): DashboardKpi => {
  const projects = listProjects();
  const wkStart = startOfWeek(today);
  const wkEnd = endOfWeek(today);
  const logs = listLogs();
  return {
    totalProjects: projects.length,
    activeProjects: projects.filter((p) => p.status === 'active').length,
    completedProjects: projects.filter((p) => p.status === 'completed').length,
    totalMembers: listMembers().length,
    todayLogs: logs.filter((l) => l.date === today).length,
    weekLogs: logs.filter((l) => l.date >= wkStart && l.date <= wkEnd).length,
  };
};

/* ── Seed sample data (idempotent, first-run only) ─ */

export const seedIfEmpty = (): void => {
  if (listProjects().length > 0 || listMembers().length > 0 || listLogs().length > 0) return;
  const m1 = saveMember({ name: '양희성', role: 'PM' });
  const m2 = saveMember({ name: '김연구', role: '연구원' });
  const m3 = saveMember({ name: '이개발', role: '개발자' });

  const today = new Date();
  const ymd = (offset: number): string => {
    const d = new Date(today);
    d.setDate(d.getDate() + offset);
    return toIsoDate(d);
  };

  const p1 = saveProject({
    name: '전력계통 해석 솔루션 고도화',
    description: '발송전 계통 시뮬레이션 엔진 성능 개선',
    startDate: ymd(-30),
    memberIds: [m1.id, m2.id],
    status: 'active',
  });
  const p2 = saveProject({
    name: 'AI 모델 파인튜닝 파이프라인',
    description: '운영 로그 기반 LLM 파인튜닝 자동화',
    startDate: ymd(-20),
    memberIds: [m1.id, m3.id],
    status: 'active',
  });
  saveProject({
    name: '구버전 운영 도구 유지보수',
    description: '레거시 C# 유틸 버그 패치',
    startDate: ymd(-60),
    memberIds: [m3.id],
    status: 'active',
  });

  saveLog({ projectId: p1.id, memberId: m1.id, date: ymd(-5), items: ['요구사항 정의 회의 진행', '범위 합의서 초안 작성'], hours: 4, progress: 10 });
  saveLog({ projectId: p1.id, memberId: m2.id, date: ymd(-3), items: ['전력계통 데이터 샘플 수집', '기존 엔진 벤치마크 측정'], hours: 6, progress: 25 });
  saveLog({ projectId: p1.id, memberId: m1.id, date: ymd(-1), items: ['엔진 모듈 리팩토링 설계', '리뷰 일정 공유'], hours: 5, progress: 35 });
  saveLog({ projectId: p2.id, memberId: m3.id, date: ymd(-4), items: ['데이터셋 정제 스크립트 작성', '학습 베이스라인 확보'], hours: 7, progress: 20 });
  saveLog({ projectId: p2.id, memberId: m1.id, date: ymd(-2), items: ['파인튜닝 파라미터 비교 실험', '평가 메트릭 정의'], hours: 4, progress: 30 });
};
