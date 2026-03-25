import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { enrollmentsAPI } from '../../api/enrollments';
import { useAuth } from '../../hooks/useAuth';
import Navbar from '../../components/layout/Navbar';
import LoadingSpinner from '../../components/common/LoadingSpinner';

function MyCourses() {
  const navigate = useNavigate();
  useAuth();

  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, in_progress, completed, not_started

  useEffect(() => {
    fetchMyCourses();
  }, []);

  const fetchMyCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await enrollmentsAPI.getMyCourses();
      setEnrollments(data.enrollments || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load courses');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (progressPercentage) => {
    if (progressPercentage === 0) {
      return { label: 'Not Started', color: 'bg-gray-100 text-gray-700' };
    } else if (progressPercentage === 100) {
      return { label: 'Completed', color: 'bg-green-100 text-green-700' };
    } else {
      return { label: 'In Progress', color: 'bg-blue-100 text-blue-700' };
    }
  };

  const getFilteredEnrollments = () => {
    if (filter === 'all') return enrollments;

    return enrollments.filter(enrollment => {
      const progress = enrollment.progress_percentage || 0;
      
      if (filter === 'not_started') return progress === 0;
      if (filter === 'in_progress') return progress > 0 && progress < 100;
      if (filter === 'completed') return progress === 100;
      
      return true;
    });
  };

  const filteredEnrollments = getFilteredEnrollments();

  // Calculate statistics
  const totalCourses = enrollments.length;
  const completedCourses = enrollments.filter(e => (e.progress_percentage || 0) === 100).length;
  const inProgressCourses = enrollments.filter(e => {
    const p = e.progress_percentage || 0;
    return p > 0 && p < 100;
  }).length;
  const notStartedCourses = enrollments.filter(e => (e.progress_percentage || 0) === 0).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <LoadingSpinner text="Loading your courses..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg max-w-md">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
          <button 
            onClick={fetchMyCourses}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
    <Navbar />
    
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">My Courses</h1>
          <p className="text-gray-600 mt-1">Track your learning progress</p>
        </div>
      </div>
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-gray-800">{totalCourses}</div>
            <div className="text-sm text-gray-600 mt-1">Total Enrolled</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-blue-600">{inProgressCourses}</div>
            <div className="text-sm text-gray-600 mt-1">In Progress</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-green-600">{completedCourses}</div>
            <div className="text-sm text-gray-600 mt-1">Completed</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-gray-400">{notStartedCourses}</div>
            <div className="text-sm text-gray-600 mt-1">Not Started</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All ({totalCourses})
            </button>
            <button
              onClick={() => setFilter('in_progress')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'in_progress'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              In Progress ({inProgressCourses})
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'completed'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Completed ({completedCourses})
            </button>
            <button
              onClick={() => setFilter('not_started')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'not_started'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Not Started ({notStartedCourses})
            </button>
          </div>
        </div>

        {/* Empty State */}
        {enrollments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No courses yet
            </h2>
            <p className="text-gray-500 mb-6">
              Start your learning journey by enrolling in a course
            </p>
            <button
              onClick={() => navigate('/courses')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Browse Courses
            </button>
          </div>
        ) : filteredEnrollments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No courses in this category
            </h2>
            <p className="text-gray-500">
              Try selecting a different filter
            </p>
          </div>
        ) : (
          /* Course List */
          <div className="space-y-4">
            {filteredEnrollments.map((enrollment) => {
              const course = enrollment.course;
              const progress = enrollment.progress_percentage || 0;
              const status = getStatusBadge(progress);
              
              return (
                <div
                  key={enrollment.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-800">
                            {course.title}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${status.color}`}>
                            {status.label}
                          </span>
                        </div>
                        
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {course.description}
                        </p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>📖 {enrollment.total_lessons || 0} lessons</span>
                          <span>✓ {enrollment.completed_lessons || 0} completed</span>
                          <span>👤 {course.instructor_name}</span>
                        </div>
                      </div>

                      <div className="ml-6 flex flex-col items-end space-y-2">
                        {progress > 0 ? (
                          <button
                            onClick={() => navigate(`/courses/${course.id}/learn`)}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                          >
                            Continue Learning
                          </button>
                        ) : (
                          <button
                            onClick={() => navigate(`/courses/${course.id}/learn`)}
                            className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
                          >
                            Start Course
                          </button>
                        )}
                        
                        <button
                          onClick={() => navigate(`/courses/${course.id}`)}
                          className="text-sm text-gray-600 hover:text-blue-600 transition"
                        >
                          View Details
                        </button>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-600 font-medium">Progress</span>
                        <span className="text-gray-800 font-semibold">{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all ${
                            progress === 100 ? 'bg-green-600' : 'bg-blue-600'
                          }`}
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default MyCourses;