import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { coursesAPI } from '../../api/courses';
import { enrollmentsAPI } from '../../api/enrollments';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../context/ToastContext';
import Navbar from '../../components/layout/Navbar';
import LoadingSpinner from '../../components/common/LoadingSpinner';

function CourseDetail() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  useAuth();

  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enrolling, setEnrolling] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    fetchCourse();
  }, [courseId]);

  const fetchCourse = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await coursesAPI.getCourse(courseId);
      setCourse(data);

      // TODO: Check if user is enrolled (we'll implement this properly later)
      setIsEnrolled(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load course');
      console.error('Error fetching course:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    try {
      setEnrolling(true);
      await enrollmentsAPI.enroll(course.id);
      setIsEnrolled(true);
      showToast('Successfully enrolled in course!', 'success');
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to enroll', 'error');
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <LoadingSpinner text="Loading course details..." />
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
            onClick={() => navigate('/courses')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Back to Courses
          </button>
        </div>
      </div>
    );
  }

  if (!course) return null;

  return (
    <div className="min-h-screen bg-gray-100">
    <Navbar />
    
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Remove "Back to Courses" button - navigation is in navbar now */}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Left Side */}
          <div className="lg:col-span-2 space-y-6">
            {/* Course Header */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h1 className="text-4xl font-bold text-gray-800 mb-4">
                {course.title}
              </h1>
              
              <p className="text-lg text-gray-600 mb-6">
                {course.description}
              </p>

              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <span className="text-xl mr-2">👤</span>
                  {course.instructor_name}
                </span>
                <span className="flex items-center">
                  <span className="text-xl mr-2">📖</span>
                  {course.lesson_count} lessons
                </span>
                <span className="flex items-center">
                  <span className="text-xl mr-2">👥</span>
                  {course.enrollment_count} students
                </span>
              </div>
            </div>

            {/* Course Content */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                Course Content
              </h2>

              {course.lessons && course.lessons.length > 0 ? (
                <div className="space-y-3">
                  {course.lessons.map((lesson, index) => (
                    <div
                      key={lesson.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                          {index + 1}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-800">
                            {lesson.title}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {lesson.content_type} • {lesson.duration_minutes} min
                          </p>
                        </div>
                      </div>
                      
                      {isEnrolled && (
                        <button
                          onClick={() => navigate(`/courses/${course.id}/learn`)}
                          className="text-blue-600 hover:text-blue-700 font-medium">
                          Start →
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No lessons available yet.</p>
              )}
            </div>
          </div>

          {/* Sidebar - Right Side */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
              {/* Course Image */}
              <div className="w-full h-48 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg mb-6 flex items-center justify-center">
                {course.thumbnail_url ? (
                  <img 
                    src={course.thumbnail_url} 
                    alt={course.title}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="text-white text-6xl">📚</div>
                )}
              </div>

              {/* Enrollment Action */}
              {isEnrolled ? (
                <button
                  onClick={() => navigate(`/courses/${course.id}/learn`)}
                  className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition mb-4"
                >
                  Continue Learning
                </button>
              ) : (
                <button
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed mb-4"
                >
                  {enrolling ? 'Enrolling...' : 'Enroll Now'}
                </button>
              )}

              {/* Course Info */}
              <div className="border-t pt-4 space-y-3">
                <div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-1">
                    Instructor
                  </h3>
                  <p className="text-gray-800">{course.instructor_name}</p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-1">
                    Duration
                  </h3>
                  <p className="text-gray-800">
                    {course.lessons?.reduce((total, lesson) => total + (lesson.duration_minutes || 0), 0)} minutes
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-1">
                    Level
                  </h3>
                  <p className="text-gray-800">All Levels</p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-1">
                    Language
                  </h3>
                  <p className="text-gray-800">English</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetail;