import { Link } from 'react-router-dom';
import type { ReactElement } from 'react';

const NotFound = (): ReactElement => {
  return (
    <div className="wl-container">
      <div className="wl-empty">
        <h1 style={{ fontSize: 60, margin: 0, color: 'var(--accent, #1B2A4A)' }}>404</h1>
        <h3>페이지를 찾을 수 없습니다</h3>
        <p>요청하신 경로가 존재하지 않습니다.</p>
        <Link to="/" className="wl-btn wl-btn-primary">대시보드로 돌아가기</Link>
      </div>
    </div>
  );
};

export default NotFound;
