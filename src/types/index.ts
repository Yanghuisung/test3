/* ────────────────────────────────────────────
 *  Domain types for the work-log system
 * ──────────────────────────────────────────── */

export type ProjectStatus = 'active' | 'paused' | 'completed';

export interface Project {
  id: string;
  name: string;
  description?: string;
  startDate: string;   // YYYY-MM-DD
  endDate?: string;    // YYYY-MM-DD
  memberIds: string[];
  status: ProjectStatus;
  createdAt: string;   // ISO
}

export interface Member {
  id: string;
  name: string;
  role?: string;
  email?: string;
  createdAt: string;
}

export interface WorkLog {
  id: string;
  projectId: string;
  memberId: string;
  date: string;        // YYYY-MM-DD
  items: string[];     // 개조식 항목
  hours?: number;
  progress?: number;   // 작성 시점 프로젝트 진척도(0-100)
  createdAt: string;
  updatedAt: string;
}

/* ────────────────────────────────────────────
 *  Theme / Toast / Site config (kept from template)
 * ──────────────────────────────────────────── */

export type ThemeMode = 'auto' | 'light' | 'dark';
export type ColorTheme = 'blue' | 'red' | 'green' | 'purple' | 'orange';

export type ToastType = 'info' | 'success' | 'error' | 'warning';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

export interface BrandPart {
  text: string;
  className: string;
}

export interface SubMenuItem {
  path: string;
  label: string;
}

export interface MenuItem {
  path: string;
  label: string;
  activePath?: string;
  dropdown?: SubMenuItem[];
}

export interface FamilySite {
  name: string;
  url: string;
}

export interface ColorOption {
  name: ColorTheme;
  color: string;
}

export interface CompanyInfo {
  name: string;
  ceo?: string;
  email?: string;
  phone?: string;
  address?: string;
  businessHours?: string;
}

export interface SiteConfig {
  id: string;
  name: string;
  nameKo: string;
  description: string;
  themeColor: string;
  brand: { parts: BrandPart[] };
  company: CompanyInfo;
  colors: ColorOption[];
  menuItems: MenuItem[];
  footerLinks: { path: string; label: string }[];
}
