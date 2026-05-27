import { supabase } from '../lib/supabase';
import type { Project, Member, WorkLog, ProjectStatus } from '../types';

/* ── Row → App type mappers ───────────────── */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toProject = (r: any): Project => ({
  id: r.id,
  name: r.name,
  description: r.description ?? undefined,
  startDate: r.start_date,
  endDate: r.end_date ?? undefined,
  memberIds: (r.member_ids as string[]) ?? [],
  status: r.status as ProjectStatus,
  createdAt: r.created_at,
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toMember = (r: any): Member => ({
  id: r.id,
  name: r.name,
  role: r.role ?? undefined,
  email: r.email ?? undefined,
  createdAt: r.created_at,
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toWorkLog = (r: any): WorkLog => ({
  id: r.id,
  projectId: r.project_id,
  memberId: r.member_id,
  date: r.date,
  items: (r.items as string[]) ?? [],
  hours: r.hours ?? undefined,
  progress: r.progress ?? undefined,
  createdAt: r.created_at,
  updatedAt: r.updated_at,
});

/* ── Projects ─────────────────────────────── */

export const listProjects = async (): Promise<Project[]> => {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .order('created_at');
  if (error) throw error;
  return (data ?? []).map(toProject);
};

export const getProject = async (id: string): Promise<Project | undefined> => {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('id', id)
    .single();
  if (error) {
    if (error.code === 'PGRST116') return undefined;
    throw error;
  }
  return toProject(data);
};

export const saveProject = async (
  input: Omit<Project, 'id' | 'createdAt'> & { id?: string }
): Promise<Project> => {
  const payload = {
    name: input.name,
    description: input.description ?? null,
    start_date: input.startDate,
    end_date: input.endDate ?? null,
    member_ids: input.memberIds,
    status: input.status,
  };
  if (input.id) {
    const { data, error } = await supabase
      .from('projects')
      .update(payload)
      .eq('id', input.id)
      .select()
      .single();
    if (error) throw error;
    return toProject(data);
  }
  const { data, error } = await supabase
    .from('projects')
    .insert(payload)
    .select()
    .single();
  if (error) throw error;
  return toProject(data);
};

export const deleteProject = async (id: string): Promise<void> => {
  const { error } = await supabase.from('projects').delete().eq('id', id);
  if (error) throw error;
  // work_logs are cascade-deleted via FK
};

/* ── Members ──────────────────────────────── */

export const listMembers = async (): Promise<Member[]> => {
  const { data, error } = await supabase
    .from('members')
    .select('*')
    .order('created_at');
  if (error) throw error;
  return (data ?? []).map(toMember);
};

export const getMember = async (id: string): Promise<Member | undefined> => {
  const { data, error } = await supabase
    .from('members')
    .select('*')
    .eq('id', id)
    .single();
  if (error) {
    if (error.code === 'PGRST116') return undefined;
    throw error;
  }
  return toMember(data);
};

export const saveMember = async (
  input: Omit<Member, 'id' | 'createdAt'> & { id?: string }
): Promise<Member> => {
  const payload = {
    name: input.name,
    role: input.role ?? null,
    email: input.email ?? null,
  };
  if (input.id) {
    const { data, error } = await supabase
      .from('members')
      .update(payload)
      .eq('id', input.id)
      .select()
      .single();
    if (error) throw error;
    return toMember(data);
  }
  const { data, error } = await supabase
    .from('members')
    .insert(payload)
    .select()
    .single();
  if (error) throw error;
  return toMember(data);
};

export const deleteMember = async (id: string): Promise<void> => {
  // member_ids 배열에서 해당 멤버 제거
  const { data: affected, error: fetchErr } = await supabase
    .from('projects')
    .select('id, member_ids')
    .contains('member_ids', [id]);
  if (fetchErr) throw fetchErr;
  for (const p of affected ?? []) {
    await supabase
      .from('projects')
      .update({ member_ids: (p.member_ids as string[]).filter((mid: string) => mid !== id) })
      .eq('id', p.id);
  }
  // work_logs는 FK ON DELETE CASCADE로 자동 처리
  const { error } = await supabase.from('members').delete().eq('id', id);
  if (error) throw error;
};

/* ── Work Logs ────────────────────────────── */

export const listLogs = async (): Promise<WorkLog[]> => {
  const { data, error } = await supabase
    .from('work_logs')
    .select('*')
    .order('date');
  if (error) throw error;
  return (data ?? []).map(toWorkLog);
};

export const logsByProject = async (projectId: string): Promise<WorkLog[]> => {
  const { data, error } = await supabase
    .from('work_logs')
    .select('*')
    .eq('project_id', projectId)
    .order('date');
  if (error) throw error;
  return (data ?? []).map(toWorkLog);
};

export const getLog = async (id: string): Promise<WorkLog | undefined> => {
  const { data, error } = await supabase
    .from('work_logs')
    .select('*')
    .eq('id', id)
    .single();
  if (error) {
    if (error.code === 'PGRST116') return undefined;
    throw error;
  }
  return toWorkLog(data);
};

export const saveLog = async (
  input: Omit<WorkLog, 'id' | 'createdAt' | 'updatedAt'> & { id?: string }
): Promise<WorkLog> => {
  const now = new Date().toISOString();
  const payload = {
    project_id: input.projectId,
    member_id: input.memberId,
    date: input.date,
    items: input.items,
    hours: input.hours ?? null,
    progress: input.progress ?? null,
    updated_at: now,
  };
  if (input.id) {
    const { data, error } = await supabase
      .from('work_logs')
      .update(payload)
      .eq('id', input.id)
      .select()
      .single();
    if (error) throw error;
    return toWorkLog(data);
  }
  const { data, error } = await supabase
    .from('work_logs')
    .insert(payload)
    .select()
    .single();
  if (error) throw error;
  return toWorkLog(data);
};

export const deleteLog = async (id: string): Promise<void> => {
  const { error } = await supabase.from('work_logs').delete().eq('id', id);
  if (error) throw error;
};

/* ── Seed (첫 실행 샘플 데이터) ─────────────── */

const ymd = (base: Date, offset: number): string => {
  const d = new Date(base);
  d.setDate(d.getDate() + offset);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

// React StrictMode에서 useEffect가 두 번 호출되는 것을 방지하는 모듈 레벨 플래그
let _seeding = false;

export const seedIfEmpty = async (): Promise<void> => {
  if (_seeding) return;
  _seeding = true;
  try {
  const [projects, members] = await Promise.all([listProjects(), listMembers()]);
  if (projects.length > 0 || members.length > 0) return;

  const today = new Date();
  const [m1, m2, m3] = await Promise.all([
    saveMember({ name: '양희성', role: 'PM' }),
    saveMember({ name: '김연구', role: '연구원' }),
    saveMember({ name: '이개발', role: '개발자' }),
  ]);

  const [p1, p2] = await Promise.all([
    saveProject({
      name: '전력계통 해석 솔루션 고도화',
      description: '발송전 계통 시뮬레이션 엔진 성능 개선',
      startDate: ymd(today, -30),
      memberIds: [m1.id, m2.id],
      status: 'active',
    }),
    saveProject({
      name: 'AI 모델 파인튜닝 파이프라인',
      description: '운영 로그 기반 LLM 파인튜닝 자동화',
      startDate: ymd(today, -20),
      memberIds: [m1.id, m3.id],
      status: 'active',
    }),
    saveProject({
      name: '구버전 운영 도구 유지보수',
      description: '레거시 C# 유틸 버그 패치',
      startDate: ymd(today, -60),
      memberIds: [m3.id],
      status: 'active',
    }),
  ]);

  await Promise.all([
    saveLog({ projectId: p1.id, memberId: m1.id, date: ymd(today, -5), items: ['요구사항 정의 회의 진행', '범위 합의서 초안 작성'], hours: 4, progress: 10 }),
    saveLog({ projectId: p1.id, memberId: m2.id, date: ymd(today, -3), items: ['전력계통 데이터 샘플 수집', '기존 엔진 벤치마크 측정'], hours: 6, progress: 25 }),
    saveLog({ projectId: p1.id, memberId: m1.id, date: ymd(today, -1), items: ['엔진 모듈 리팩토링 설계', '리뷰 일정 공유'], hours: 5, progress: 35 }),
    saveLog({ projectId: p2.id, memberId: m3.id, date: ymd(today, -4), items: ['데이터셋 정제 스크립트 작성', '학습 베이스라인 확보'], hours: 7, progress: 20 }),
    saveLog({ projectId: p2.id, memberId: m1.id, date: ymd(today, -2), items: ['파인튜닝 파라미터 비교 실험', '평가 메트릭 정의'], hours: 4, progress: 30 }),
  ]);
  } finally {
    _seeding = false;
  }
};
