import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { coursesAPI } from '../../api/courses';
import { useToast } from '../../context/ToastContext';
import Navbar from '../../components/layout/Navbar';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import PageTransition from '../../components/common/PageTransition';

function ManagerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await coursesAPI.getAllCourses();
      // Filter to show only courses created by this manager
      const myCourses = data.courses || [];
      setCourses(myCourses);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load courses');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      return;
    }

    try {
      await coursesAPI.deleteCourse(courseId);
      showToast('Course deleted successfully', 'success');
      fetchCourses(); // Refresh list
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to delete course', 'error');
    }
  };

  const handleTogglePublish = async (course) => {
    try {
      if (course.is_published) {
        await coursesAPI.updateCourse(course.id, { is_published: false });
        showToast('Course unpublished', 'info');
      } else {
        // Check if course has lessons
        if (!course.lesson_count || course.lesson_count === 0) {
          showToast('Cannot publish: Course must have at least one lesson', 'error');
          return;
        }
        await coursesAPI.updateCourse(course.id, { is_published: true });
        showToast('Course published successfully!', 'success');
      }
      fetchCourses(); // Refresh list
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to update course', 'error');
    }
  };

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
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
            <button 
              onClick={fetchCourses}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const publishedCourses = courses.filter(c => c.is_published).length;
  const draftCourses = courses.filter(c => !c.is_published).length;
  const totalEnrollments = courses.reduce((sum, c) => sum + (c.enrollment_count || 0), 0);

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Manager Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage your courses and content</p>
            </div>
            <button
              onClick={() => navigate('/manager/courses/create')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              + Create New Course
            </button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-3xl font-bold text-gray-800">{courses.length}</div>
              <div className="text-sm text-gray-600 mt-1">Total Courses</div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-3xl font-bold text-green-600">{publishedCourses}</div>
              <div className="text-sm text-gray-600 mt-1">Published</div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-3xl font-bold text-yellow-600">{draftCourses}</div>
              <div className="text-sm text-gray-600 mt-1">Drafts</div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-3xl font-bold text-blue-600">{totalEnrollments}</div>
              <div className="text-sm text-gray-600 mt-1">Total Enrollments</div>
            </div>
          </div>

          {/* Courses List */}
          {courses.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="text-6xl mb-4">📚</div>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                No courses yet
              </h2>
              <p className="text-gray-500 mb-6">
                Create your first course to get started
              </p>
              <button
                onClick={() => navigate('/manager/courses/create')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                Create Course
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Your Courses</h2>
              
              {courses.map((course) => (
                <div
                  key={course.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          {course.title}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          course.is_published
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {course.is_published ? 'Published' : 'Draft'}
                        </span>
                      </div>
                      
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {course.description}
                      </p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>📖 {course.lesson_count || 0} lessons</span>
                        <span>👥 {course.enrollment_count || 0} students</span>
                        <span>📅 Created {new Date(course.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="ml-6 flex flex-col space-y-2">
                      <button
                        onClick={() => navigate(`/manager/courses/${course.id}/edit`)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition"
                      >
                        Edit Course
                      </button>
                      
                      <button
                        onClick={() => navigate(`/manager/courses/${course.id}/lessons`)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-semibold hover:bg-purple-700 transition"
                      >
                        Manage Lessons
                      </button>
                      
                      <button
                        onClick={() => handleTogglePublish(course)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                          course.is_published
                            ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                            : 'bg-green-600 text-white hover:bg-green-700'
                        }`}
                      >
                        {course.is_published ? 'Unpublish' : 'Publish'}
                      </button>
                      
                      <button
                        onClick={() => navigate(`/courses/${course.id}`)}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-300 transition"
                      >
                        View as Student
                      </button>
                      
                      <button
                        onClick={() => handleDeleteCourse(course.id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}

export default ManagerDashboard;