import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import MainLayout from "./layouts/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import ProfileGate from "./components/ProfileGate";
import ErrorBoundary from "./components/ErrorBoundary";
import HomePage from "./pages/HomePage";
import JobsPage from "./pages/JobsPage";
import JobDetailPage from "./pages/JobDetailPage";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import RoadmapPage from "./pages/RoadmapPage";
import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <MainLayout>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/jobs" element={<ErrorBoundary fallbackMessage="Failed to load jobs"><JobsPage /></ErrorBoundary>} />
              <Route path="/jobs/:jobId" element={<ErrorBoundary fallbackMessage="Failed to load job details"><JobDetailPage /></ErrorBoundary>} />
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ErrorBoundary fallbackMessage="Failed to load profile">
                      <ProfilePage />
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmap"
                element={
                  <ProtectedRoute>
                    <ProfileGate>
                      <ErrorBoundary fallbackMessage="Failed to load roadmaps">
                        <RoadmapPage />
                      </ErrorBoundary>
                    </ProfileGate>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </ErrorBoundary>
        </MainLayout>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
