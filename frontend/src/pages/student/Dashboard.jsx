import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/layout/Navbar';
import PageTransition from '../../components/common/PageTransition';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Welcome, {user?.first_name}!
            </h2>
            <div className="space-y-2 text-gray-600">
              <p><strong>Email:</strong> {user?.email}</p>
              <p><strong>Role:</strong> {user?.role}</p>
              <p><strong>Company:</strong> {user?.company?.name}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button
              onClick={() => navigate('/courses')}
              className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 transition text-left"
            >
              <div className="text-4xl mb-2">📚</div>
              <h3 className="text-xl font-semibold mb-1">Browse Courses</h3>
              <p className="text-blue-100">Explore available learning content</p>
            </button>

            <button
              onClick={() => navigate('/my-courses')}
              className="bg-green-600 text-white p-6 rounded-lg hover:bg-green-700 transition text-left"
            >
              <div className="text-4xl mb-2">🎓</div>
              <h3 className="text-xl font-semibold mb-1">My Courses</h3>
              <p className="text-green-100">Continue your learning journey</p>
            </button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}

export default Dashboard;