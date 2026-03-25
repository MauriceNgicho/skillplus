import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { coursesAPI } from '../../api/courses';
import { useToast } from '../../context/ToastContext';
import { lessonsAPI } from '../../api/lessons';
import Navbar from '../../components/layout/Navbar';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import PageTransition from '../../components/common/PageTransition';

function ManageLessons() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingLesson, setEditingLesson] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    content_type: 'video',
    duration_minutes: '',
    description: '',
  });
  const [formErrors, setFormErrors] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchCourse();
  }, [courseId]);

  const fetchCourse = async () => {
    try {
      setLoading(true);
      const data = await coursesAPI.getCourse(courseId);
      setCourse(data);
      setLessons(data.lessons || []);
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to load course', 'error');
      navigate('/manager/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = (hideForm = true) => {
    setFormData({
      title: '',
      content_type: 'video',
      duration_minutes: '',
      description: '',
    });
    setFormErrors({});
    setEditingLesson(null);
    setSelectedFile(null);
    if (hideForm) {
      setShowAddForm(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateLessonForm = () => {
    const errors = {};

    if (!formData.title.trim()) {
      errors.title = 'Lesson title is required';
    }

    if (!formData.duration_minutes || formData.duration_minutes < 1) {
      errors.duration_minutes = 'Duration must be at least 1 minute';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleAddLesson = () => {
    setFormData({
      title: '',
      content_type: 'video',
      duration_minutes: '',
      description: '',
    });
    setFormErrors({});
    setEditingLesson(null);
    setSelectedFile(null);
    setShowAddForm(true);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Auto-detect content type based on file extension
      const fileName = file.name.toLowerCase();
      if (fileName.match(/\.(mp4|avi|mov|mkv|webm)$/)) {
        setFormData(prev => ({ ...prev, content_type: 'video' }));
      } else if (fileName.match(/\.(pdf|doc|docx|xls|xlsx|ppt|pptx)$/)) {
        setFormData(prev => ({ ...prev, content_type: 'document' }));
      }
    }
  };

  const handleEditLesson = (lesson) => {
    setEditingLesson(lesson);
    setFormData({
      title: lesson.title,
      content_type: lesson.content_type,
      duration_minutes: lesson.duration_minutes || '',
      description: lesson.description || '',
    });
    setShowAddForm(true);
  };

  const handleSubmitLesson = async (e) => {
    e.preventDefault();

    if (!validateLessonForm()) {
      return;
    }

    try {
      setUploading(true);
      
      const lessonData = {
        title: formData.title.trim(),
        content_type: formData.content_type,
        duration_minutes: parseInt(formData.duration_minutes),
        description: formData.description.trim(),
      };

      let createdOrUpdatedLesson;

      if (editingLesson) {
        // Update existing lesson
        createdOrUpdatedLesson = await lessonsAPI.updateLesson(editingLesson.id, lessonData);
        showToast('Lesson updated successfully!', 'success');
      } else {
        // Create new lesson
        const result = await lessonsAPI.createLesson(courseId, lessonData);
        createdOrUpdatedLesson = result.lesson;
        showToast('Lesson created successfully!', 'success');
      }

      // Upload file if selected
      if (selectedFile && createdOrUpdatedLesson) {
        try {
          const lessonId = createdOrUpdatedLesson.id;
          await lessonsAPI.uploadLessonFile(lessonId, selectedFile);
          showToast('File uploaded successfully!', 'success');
        } catch (uploadErr) {
          const errorMessage = uploadErr.response?.data?.error || 'File upload failed';
          showToast(`Lesson saved, but ${errorMessage}`, 'warning');
          console.error('Upload error:', uploadErr);
        }
      }

      resetForm();
      fetchCourse();
    } catch (err) {
      console.error('Error saving lesson:', err);
      showToast(err.response?.data?.error || 'Failed to save lesson', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Are you sure you want to delete this lesson?')) {
      return;
    }

    try {
      await lessonsAPI.deleteLesson(lessonId);
      showToast('Lesson deleted successfully!', 'success');
      fetchCourse();
    } catch (err) {
      console.error('Error deleting lesson:', err);
      showToast(err.response?.data?.error || 'Failed to delete lesson', 'error');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <LoadingSpinner text="Loading course..." />
      </div>
    );
  }

  if (!course) return null;

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        
        <div className="max-w-5xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => navigate('/manager/dashboard')}
              className="text-blue-600 hover:text-blue-700 font-medium mb-4"
            >
              ← Back to Dashboard
            </button>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-800">{course.title}</h1>
                <p className="text-gray-600 mt-1">Manage course lessons</p>
              </div>
              <button
                onClick={handleAddLesson}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                + Add Lesson
              </button>
            </div>
          </div>

          {/* Add/Edit Lesson Form */}
          {showAddForm && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">
                {editingLesson ? 'Edit Lesson' : 'Add New Lesson'}
              </h2>
              
              <form onSubmit={handleSubmitLesson} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Lesson Title */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Lesson Title *
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleFormChange}
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none ${
                        formErrors.title ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="e.g., Introduction to Variables"
                    />
                    {formErrors.title && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.title}</p>
                    )}
                  </div>

                  {/* Content Type */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Content Type
                    </label>
                    <select
                      name="content_type"
                      value={formData.content_type}
                      onChange={handleFormChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      <option value="video">Video</option>
                      <option value="text">Text</option>
                      <option value="quiz">Quiz</option>
                      <option value="document">Document</option>
                    </select>
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Duration (minutes) *
                    </label>
                    <input
                      type="number"
                      name="duration_minutes"
                      value={formData.duration_minutes}
                      onChange={handleFormChange}
                      min="1"
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none ${
                        formErrors.duration_minutes ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="30"
                    />
                    {formErrors.duration_minutes && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.duration_minutes}</p>
                    )}
                  </div>

                  {/* File Upload */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Upload Content File (optional)
                    </label>
                    <div className="flex items-center space-x-4">
                      <label className="flex-1">
                        <input
                          type="file"
                          onChange={handleFileChange}
                          accept=".mp4,.mov,.avi,.mkv,.webm,.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                      </label>
                    </div>
                    {selectedFile && (
                      <div className="mt-2 flex items-center space-x-2 text-sm text-gray-600">
                        <span className="font-medium">Selected:</span>
                        <span>{selectedFile.name}</span>
                        <span className="text-gray-400">({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</span>
                        <button
                          type="button"
                          onClick={() => setSelectedFile(null)}
                          className="text-red-600 hover:text-red-700 ml-2"
                        >
                          ✕ Remove
                        </button>
                      </div>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      Supported: Videos (mp4, mov, avi, mkv, webm), Documents (pdf, doc, docx, ppt, pptx, xls, xlsx)
                    </p>
                  </div>

                  {/* Description */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Description (optional)
                    </label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleFormChange}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                      placeholder="Describe what this lesson covers..."
                    />
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploading 
                      ? (selectedFile ? 'Uploading...' : 'Saving...') 
                      : (editingLesson ? 'Update Lesson' : 'Add Lesson')
                    }
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Lessons List */}
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-800">
                Course Lessons ({lessons.length})
              </h2>
            </div>

            {lessons.length === 0 ? (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4">📖</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No lessons yet
                </h3>
                <p className="text-gray-500 mb-6">
                  Add your first lesson to get started
                </p>
                <button
                  onClick={handleAddLesson}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  Add Lesson
                </button>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {lessons.map((lesson, index) => (
                  <div
                    key={lesson.id}
                    className="p-6 hover:bg-gray-50 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold flex-shrink-0">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-800 mb-1">
                            {lesson.title}
                          </h3>
                          {lesson.description && (
                            <p className="text-sm text-gray-600 mb-2">
                              {lesson.description}
                            </p>
                          )}
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span className="capitalize">📹 {lesson.content_type}</span>
                            <span>⏱️ {lesson.duration_minutes} min</span>
                            {lesson.content_url && (
                              <span className="text-green-600">✓ File uploaded</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => handleEditLesson(lesson)}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium hover:bg-blue-200 transition"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteLesson(lesson.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm font-medium hover:bg-red-200 transition"
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
      </div>
    </PageTransition>
  );
}

export default ManageLessons;