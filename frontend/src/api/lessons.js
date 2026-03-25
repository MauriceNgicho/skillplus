import api from './axios';

export const lessonsAPI = {
  // Get all lessons for a course
  getCourseLessons: async (courseId) => {
    const response = await api.get(`/courses/${courseId}/lessons`);
    return response.data;
  },

  // Get single lesson
  getLesson: async (lessonId) => {
    const response = await api.get(`/lessons/${lessonId}`);
    return response.data;
  },

  // Create lesson
  createLesson: async (courseId, lessonData) => {
    const response = await api.post(`/courses/${courseId}/lessons`, lessonData);
    return response.data;
  },

  // Update lesson
  updateLesson: async (lessonId, lessonData) => {
    const response = await api.put(`/lessons/${lessonId}`, lessonData);
    return response.data;
  },

  // upload file for lesson
  uploadLessonFile: async (lessonId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/lessons/${lessonId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete lesson
  deleteLesson: async (lessonId) => {
    const response = await api.delete(`/lessons/${lessonId}`);
    return response.data;
  },
};