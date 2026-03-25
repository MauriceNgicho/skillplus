import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { coursesAPI } from '../../api/courses';
import { useNavigate } from 'react-router-dom';
import CourseCard from '../../components/course/CourseCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Navbar from '../../components/layout/Navbar';

function CourseCatalog() {
  const navigate = useNavigate();
  // const { user } = useAuth();
  useAuth(); // Just to ensure user is authenticated, we don't need user info here yet
  
  // State
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch courses when component mounts
  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await coursesAPI.getAllCourses();
      setCourses(data.courses || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load courses');
      console.error('Error fetching courses:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter courses based on search term
  const filteredCourses = courses.filter(course =>
    course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Course Catalog</h1>
      <p className="text-gray-600 mb-8">
        Browse and enroll in available courses
      </p>

      {/* Search Bar */}
      <div className="mb-8">
        <input
          type="text"
          placeholder="Search courses..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-md px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
        />
      </div>
        

        {/* Loading State */}
        {loading && <LoadingSpinner text="Loading courses..." />}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-6">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
            <button 
              onClick={fetchCourses}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredCourses.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              {searchTerm ? 'No courses found' : 'No courses available'}
            </h2>
            <p className="text-gray-500">
              {searchTerm ? 'Try a different search term' : 'Check back later for new courses'}
            </p>
          </div>
        )}

        {/* Courses Grid */}
        {!loading && !error && filteredCourses.length > 0 && (
          <>
            <div className="mb-4 text-gray-600">
              Showing {filteredCourses.length} of {courses.length} courses
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course) => (
                <CourseCard 
                  key={course.id} 
                  course={course}
                  isEnrolled={false} // TODO: Check if user is enrolled
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default CourseCatalog;