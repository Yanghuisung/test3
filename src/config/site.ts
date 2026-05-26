import type { SiteConfig } from '../types';

const site: SiteConfig = {
  id: 'worklog',
  name: 'Worklog',
  nameKo: '업무일지 관리 시스템',
  description: '프로젝트별 일간 작업 내용과 진행 상황을 관리하고 주/월간 요약을 생성하는 시스템',

  themeColor: '#1B2A4A',

  brand: {
    parts: [
      { text: 'Work', className: 'brand-dream' },
      { text: 'Log', className: 'brand-accent' },
    ],
  },

  company: {
    name: '한전KDN 전력ICT연구원',
    email: 'yhstarpop-81@kdn.com',
  },

  colors: [
    { name: 'blue',   color: '#1B2A4A' },
    { name: 'red',    color: '#C8102E' },
    { name: 'green',  color: '#00855A' },
    { name: 'purple', color: '#5B2C8B' },
    { name: 'orange', color: '#D4760A' },
  ],

  menuItems: [
    { path: '/',          label: '대시보드',  activePath: '/' },
    { path: '/projects',  label: '프로젝트',  activePath: '/projects' },
    { path: '/members',   label: '구성원',    activePath: '/members' },
    { path: '/logs/new',  label: '일지 작성', activePath: '/logs' },
    { path: '/summary',   label: '요약',      activePath: '/summary' },
  ],

  footerLinks: [
    { path: '/',         label: '대시보드' },
    { path: '/projects', label: '프로젝트' },
    { path: '/summary',  label: '요약' },
  ],
};

export default site;
