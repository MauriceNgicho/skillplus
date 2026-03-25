import api from './axios';

export const progressAPI = {
    // Mark a lesson as complete
    markLessonComplete: async (lessonId) => {
        const response = await api.post(`/progress/lessons/${lessonId}/complete`);
        return response.data;
    },
    // Mark a lesson as incomplete
    markLessonIncomplete: async (lessonId) => {
        const response = await api.post(`/progress/lessons/${lessonId}/incomplete`);
        return response.data;
    },
    // Get progress for a specific course
    getCourseProgress: async (courseId) => {
        const response = await api.get(`/progress/courses/${courseId}`);
        return response.data;
    },
    // Get all user's progress across courses
    getMyProgress: async () => {
        const response = await api.get('/progress/my-progress');
        return response.data;
    },
};