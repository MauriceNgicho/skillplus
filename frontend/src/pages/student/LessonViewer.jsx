import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { progressAPI } from '../../api/progress';
import { useToast } from '../../context/ToastContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ContentViewer from '../../components/lesson/ContentViewer';

function LessonViewer() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [completing, setCompleting] = useState(false);

  const fetchCourseProgress = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await progressAPI.getCourseProgress(courseId);
      setCourse(data.course);
      setLessons(data.lessons || []);
      
      // Find first incomplete lesson or start at beginning
      const firstIncompleteIndex = data.lessons.findIndex(lesson => !lesson.completed);
      setCurrentLessonIndex(firstIncompleteIndex !== -1 ? firstIncompleteIndex : 0);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load course progress');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    fetchCourseProgress();
  }, [courseId, fetchCourseProgress]);

  const handleMarkComplete = async () => {
    const currentLesson = lessons[currentLessonIndex];
    if (!currentLesson) return;

    try {
      setCompleting(true);
      
      if (currentLesson.completed) {
        // Mark as incomplete
        await progressAPI.markLessonIncomplete(currentLesson.id);
      } else {
        // Mark as complete
        await progressAPI.markLessonComplete(currentLesson.id);
        showToast('Lesson completed!', 'success');
      }

      // Refresh progress
      await fetchCourseProgress();
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to update progress', 'error');
    } finally {
      setCompleting(false);
    }
  };

  const handleNext = () => {
    if (currentLessonIndex < lessons.length - 1) {
      setCurrentLessonIndex(currentLessonIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentLessonIndex > 0) {
      setCurrentLessonIndex(currentLessonIndex - 1);
    }
  };

  const handleSelectLesson = (index) => {
    setCurrentLessonIndex(index);
  };

  if (loading) {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <LoadingSpinner text="Loading course..." />
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
            onClick={() => navigate(`/courses/${courseId}`)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Back to Course
          </button>
        </div>
      </div>
    );
  }

  if (!course || lessons.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📚</div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            No lessons available
          </h2>
          <button 
            onClick={() => navigate(`/courses/${courseId}`)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Course
          </button>
        </div>
      </div>
    );
  }

  const currentLesson = lessons[currentLessonIndex];
  const completedCount = lessons.filter(l => l.completed).length;
  const progressPercentage = Math.round((completedCount / lessons.length) * 100);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Navigation Bar */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate(`/courses/${courseId}`)}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Back to Course
            </button>
            
            <div className="flex-1 mx-8">
              <h1 className="text-lg font-semibold text-gray-800 truncate">
                {course.title}
              </h1>
              <div className="flex items-center space-x-4 mt-1">
                <div className="text-sm text-gray-500">
                  Lesson {currentLessonIndex + 1} of {lessons.length}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                  <div 
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
                <div className="text-sm font-semibold text-gray-700">
                  {progressPercentage}%
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-600">
              {completedCount}/{lessons.length} completed
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3">
          {/* Content Viewer */}
            <ContentViewer lesson={currentLesson} />

              {/* Lesson Info */}
              <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800">
                  {currentLesson.title}
                </h2>
                
                {currentLesson.completed && (
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                    ✓ Completed
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                <span>📖 {currentLesson.content_type}</span>
                <span>⏱️ {currentLesson.duration_minutes} minutes</span>
              </div>

              {currentLesson.description && (
                <div className="text-gray-600 mb-6">
                  {currentLesson.description}
                </div>
              )}

              {/* Navigation and Action Buttons */}
              <div className="flex items-center justify-between pt-6 border-t">
                <button
                  onClick={handlePrevious}
                  disabled={currentLessonIndex === 0}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ← Previous
                </button>

                <button
                  onClick={handleMarkComplete}
                  disabled={completing}
                  className={`px-6 py-3 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed ${
                    currentLesson.completed
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  {completing 
                    ? 'Updating...' 
                    : currentLesson.completed 
                      ? 'Mark as Incomplete' 
                      : 'Mark as Complete'
                  }
                </button>

                <button
                  onClick={handleNext}
                  disabled={currentLessonIndex === lessons.length - 1}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next →
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar - Lesson List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-4 sticky top-24">
              <h3 className="font-bold text-gray-800 mb-4">Course Content</h3>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {lessons.map((lesson, index) => (
                  <button
                    key={lesson.id}
                    onClick={() => handleSelectLesson(index)}
                    className={`w-full text-left p-3 rounded-lg transition ${
                      index === currentLessonIndex
                        ? 'bg-blue-50 border-2 border-blue-500'
                        : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        lesson.completed
                          ? 'bg-green-500 text-white'
                          : index === currentLessonIndex
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-300 text-gray-600'
                      }`}>
                        {lesson.completed ? '✓' : index + 1}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium truncate ${
                          index === currentLessonIndex ? 'text-blue-700' : 'text-gray-700'
                        }`}>
                          {lesson.title}
                        </div>
                        <div className="text-xs text-gray-500">
                          {lesson.duration_minutes} min
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LessonViewer;