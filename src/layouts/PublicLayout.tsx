import { lazy, Suspense, useEffect, type ReactElement } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import { seedIfEmpty } from '../utils/db';

const Dashboard      = lazy(() => import('../pages/Dashboard'));
const ProjectsList   = lazy(() => import('../pages/ProjectsList'));
const ProjectDetail  = lazy(() => import('../pages/ProjectDetail'));
const ProjectForm    = lazy(() => import('../pages/ProjectForm'));
const MembersPage    = lazy(() => import('../pages/MembersPage'));
const WorkLogNew     = lazy(() => import('../pages/WorkLogNew'));
const WorkLogEdit    = lazy(() => import('../pages/WorkLogEdit'));
const SummaryPage    = lazy(() => import('../pages/SummaryPage'));
const NotFound       = lazy(() => import('../pages/NotFound'));

const Loading = (): ReactElement => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
    <div className="loading-spinner" />
  </div>
);

const PublicLayout = (): ReactElement => {
  useEffect(() => {
    seedIfEmpty().catch(console.error);
  }, []);

  return (
    <>
      <Navbar />
      <main>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/"                     element={<Dashboard />} />
            <Route path="/projects"             element={<ProjectsList />} />
            <Route path="/projects/new"         element={<ProjectForm />} />
            <Route path="/projects/:id/edit"    element={<ProjectForm />} />
            <Route path="/projects/:id"         element={<ProjectDetail />} />
            <Route path="/members"              element={<MembersPage />} />
            <Route path="/logs/new"             element={<WorkLogNew />} />
            <Route path="/logs/:id/edit"       element={<WorkLogEdit />} />
            <Route path="/summary"              element={<SummaryPage />} />
            <Route path="*"                     element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </>
  );
};

export default PublicLayout;
