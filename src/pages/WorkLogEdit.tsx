import { useEffect, useState, type ReactElement } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getLog, listProjects, listMembers, saveLog } from '../utils/db';
import { useCurrentUser } from '../contexts/CurrentUserContext';
import { useToast } from '../contexts/ToastContext';
import WorkLogForm, { type WorkLogFormData } from '../components/WorkLogForm';
import type { Project, Member, WorkLog } from '../types';

const WorkLogEdit = (): ReactElement => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentMemberId } = useCurrentUser();
  const { showToast } = useToast();

  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [logData, setLogData] = useState<WorkLog | null>(null);

  useEffect(() => {
    const load = async () => {
      const [log, p, m] = await Promise.all([getLog(id!), listProjects(), listMembers()]);
      if (!log || log.memberId !== currentMemberId) {
        setNotFound(true);
        setLoading(false);
        return;
      }
      setProjects(p);
      setMembers(m);
      setLogData(log);
      setLoading(false);
    };
    load().catch((err) => {
      console.error(err);
      showToast('데이터를 불러오는 중 오류가 발생했습니다.', 'error');
      setLoading(false);
    });
  }, [id, currentMemberId]);

  const handleSubmit = (data: WorkLogFormData) => {
    saveLog({ id, ...data })
      .then(() => {
        showToast('일지를 수정했습니다.', 'success');
        navigate(`/projects/${data.projectId}`);
      })
      .catch((err) => { console.error(err); showToast('저장 중 오류가 발생했습니다.', 'error'); });
  };

  if (loading) return <div className="wl-container"><div className="wl-empty">불러오는 중…</div></div>;

  if (notFound) return (
    <div className="wl-container">
      <div className="wl-empty">
        <h3>일지를 찾을 수 없거나 수정 권한이 없습니다</h3>
        <p className="wl-page-sub" style={{ marginBottom: 16 }}>본인이 작성한 일지만 수정할 수 있습니다. 상단 메뉴에서 사용자를 먼저 선택해 주세요.</p>
        <Link to="/" className="wl-btn">대시보드로</Link>
      </div>
    </div>
  );

  return (
    <div className="wl-container">
      <div className="wl-page-header">
        <div>
          <h1 className="wl-page-title">일지 수정</h1>
          <p className="wl-page-sub">내용을 수정하고 저장하세요.</p>
        </div>
        <Link to={`/projects/${logData?.projectId}`} className="wl-btn">프로젝트로</Link>
      </div>
      <div className="wl-section">
        {logData && (
          <WorkLogForm
            projects={projects}
            members={members}
            initialProjectId={logData.projectId}
            initialMemberId={logData.memberId}
            initialDate={logData.date}
            initialItems={logData.items.length > 0 ? logData.items : ['']}
            initialHours={logData.hours != null ? String(logData.hours) : ''}
            initialProgress={logData.progress != null ? String(logData.progress) : ''}
            onSubmit={handleSubmit}
            cancelHref={`/projects/${logData.projectId}`}
          />
        )}
      </div>
    </div>
  );
};

export default WorkLogEdit;
