import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import Login from './pages/auth/Login';
import Dashboard from './pages/student/Dashboard';
import CourseCatalog from './pages/student/CourseCatalog';
import CourseDetail from './pages/student/CourseDetail';
import LessonViewer from './pages/student/LessonViewer';
import MyCourses from './pages/student/MyCourses';
import ManagerDashboard from './pages/manager/ManagerDashboard';
import CreateCourse from './pages/manager/CreateCourse';
import EditCourse from './pages/manager/EditCourse';
import ManageLessons from './pages/manager/ManageLessons';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/courses"
            element={
              <ProtectedRoute>
                <CourseCatalog />
              </ProtectedRoute>
            }
          />

          <Route
            path="/courses/:courseId"
            element={
              <ProtectedRoute>
                <CourseDetail />
              </ProtectedRoute>
            }
          />

          <Route
            path="/courses/:courseId/learn"
            element={
              <ProtectedRoute>
                <LessonViewer />
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-courses"
            element={
              <ProtectedRoute>
                <MyCourses />
              </ProtectedRoute>
            }
          />

          <Route
            path="/manager/dashboard"
            element={
              <ProtectedRoute requiredRole={['admin', 'manager']}>
                <ManagerDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/manager/courses/create"
            element={
              <ProtectedRoute requiredRole={['admin', 'manager']}>
                <CreateCourse />
              </ProtectedRoute>
            }
          />

          <Route
            path="/manager/courses/:courseId/edit"
            element={
              <ProtectedRoute requiredRole={['admin', 'manager']}>
                <EditCourse />
              </ProtectedRoute>
            }
          />

          <Route
            path="/manager/courses/:courseId/lessons"
            element={
              <ProtectedRoute requiredRole={['admin', 'manager']}>
                <ManageLessons />
              </ProtectedRoute>
            }
          />


          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/courses" replace />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;