import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import { CurrentUserProvider } from './contexts/CurrentUserContext';
import PublicLayout from './layouts/PublicLayout';
import type { ReactElement } from 'react';

function App(): ReactElement {
  return (
    <ThemeProvider>
      <ToastProvider>
        <CurrentUserProvider>
        <Router basename={import.meta.env.BASE_URL}>
          <div className="App">
            <Routes>
              <Route path="*" element={<PublicLayout />} />
            </Routes>
          </div>
        </Router>
        </CurrentUserProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
