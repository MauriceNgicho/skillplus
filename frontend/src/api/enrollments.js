import api from './axios';

export const enrollmentsAPI = {
    // Enroll in a course
    enroll: async (courseId) => {
        const response = await api.post('/enrollments', { course_id: courseId });
        return response.data;
    },
    // Get user's enrolled courses
    getMyCourses: async () => {
        const response = await api.get('/enrollments/my-courses');
        return response.data;
    },
    // Unenroll from a course
    unenroll: async (enrollmentId) => {
        const response = await api.delete(`/enrollments/${enrollmentId}`);
        return response.data;
    },
};