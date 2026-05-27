import { useEffect, useState, type ReactElement } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { listProjects, listMembers, saveLog } from '../utils/db';
import { toIsoDate } from '../utils/storage';
import { useToast } from '../contexts/ToastContext';
import WorkLogForm, { type WorkLogFormData } from '../components/WorkLogForm';
import type { Project, Member } from '../types';

const WorkLogNew = (): ReactElement => {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { showToast } = useToast();
  const initialProjectId = params.get('projectId') ?? '';

  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);

  useEffect(() => {
    const load = async () => {
      const [p, m] = await Promise.all([listProjects(), listMembers()]);
      setProjects(p);
      setMembers(m);
    };
    load().catch((err) => { console.error(err); showToast('데이터를 불러오는 중 오류가 발생했습니다.', 'error'); });
  }, []);

  const handleSubmit = (data: WorkLogFormData) => {
    saveLog(data)
      .then(() => {
        showToast('일지를 저장했습니다.', 'success');
        navigate(`/projects/${data.projectId}`);
      })
      .catch((err) => { console.error(err); showToast('저장 중 오류가 발생했습니다.', 'error'); });
  };

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">일지 작성</h1>
          <p className="wl-page-sub">개조식으로 작업 항목을 한 줄씩 입력하세요. (Enter로 다음 항목)</p>
        </div>
        <Link to="/" className="wl-btn">대시보드로</Link>
      </div>
      <div className="wl-section">
        <WorkLogForm
          projects={projects}
          members={members}
          initialProjectId={initialProjectId}
          initialDate={toIsoDate(new Date())}
          onSubmit={handleSubmit}
          cancelHref="/"
        />
      </div>
    </div>
  );
};

export default WorkLogNew;
