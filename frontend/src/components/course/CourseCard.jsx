import { useNavigate } from 'react-router-dom';

function CourseCard({ course, isEnrolled = false }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/courses/${course.id}`);
  };

  return (
    <div 
      onClick={handleClick}
      className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow cursor-pointer overflow-hidden"
    >
      {/* Course Image/Thumbnail */}
      <div className="h-48 bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
        {course.thumbnail_url ? (
          <img 
            src={course.thumbnail_url} 
            alt={course.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-white text-6xl">📚</div>
        )}
      </div>

      {/* Course Info */}
      <div className="p-6">
        {/* Title */}
        <h3 className="text-xl font-bold text-gray-800 mb-2 line-clamp-2">
          {course.title}
        </h3>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {course.description || 'No description available'}
        </p>

        {/* Stats Row */}
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span className="flex items-center">
            📖 {course.lesson_count || 0} lessons
          </span>
          <span className="flex items-center">
            👥 {course.enrollment_count || 0} enrolled
          </span>
        </div>

        {/* Instructor */}
        <div className="text-sm text-gray-500 mb-4">
          <span className="font-medium">Instructor:</span> {course.instructor_name || 'Unknown'}
        </div>

        {/* Status Badge or Enroll Button */}
        {isEnrolled ? (
          <div className="bg-green-100 text-green-700 px-4 py-2 rounded-lg text-center font-semibold">
            ✓ Enrolled
          </div>
        ) : (
          <button 
            onClick={(e) => {
              e.stopPropagation(); // Prevent card click when button clicked
              navigate(`/courses/${course.id}`);
            }}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            View Course
          </button>
        )}
      </div>
    </div>
  );
}

export default CourseCard;