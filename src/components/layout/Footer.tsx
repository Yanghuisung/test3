import { Link } from 'react-router-dom';
import site from '../../config/site';
import type { ReactElement } from 'react';

const Footer = (): ReactElement => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <div className="footer-brand-mark">{site.name}</div>
            <p className="footer-tag">{site.description}</p>
            <div className="company-info">
              <p><strong>{site.company.name}</strong></p>
              {site.company.email && <p>{site.company.email}</p>}
            </div>
          </div>
          <div>
            <h5>바로가기</h5>
            <ul>
              {site.footerLinks.map((link, i) => (
                <li key={i}><Link to={link.path}>{link.label}</Link></li>
              ))}
            </ul>
          </div>
          <div>
            <h5>안내</h5>
            <ul>
              <li className="footer-muted">데이터는 브라우저 localStorage에 저장됩니다.</li>
              <li className="footer-muted">기기/브라우저별로 데이터가 분리됩니다.</li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>&copy; {new Date().getFullYear()} {site.company.name}</span>
          <span className="footer-version">{site.nameKo}</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
