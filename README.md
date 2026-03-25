# SkillPlus LMS

A modern, full-stack Learning Management System (LMS) built for corporate training with multi-tenant architecture, role-based access control, and comprehensive course management capabilities.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![React](https://img.shields.io/badge/React-18.0-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Overview

SkillPlus is a corporate Learning Management System designed to facilitate employee training and development. The platform supports multiple companies (multi-tenancy), role-based access control, and provides a complete learning experience from course creation to progress tracking.

**Live Demo:** [Coming Soon]

## ✨ Key Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (Admin, Manager, Employee)
- **Multi-tenant architecture** - Complete data isolation between companies
- Secure password hashing with bcrypt

### 👨‍💼 Manager Features
- **Course Creation & Management**
  - Create, edit, and delete courses
  - Upload multimedia content (videos, PDFs, documents)
  - Publish/unpublish courses
  - Organize lessons with drag-and-drop ordering
- **Content Upload**
  - Support for videos (MP4, MOV, AVI, MKV, WebM)
  - Support for documents (PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX)
  - Automatic content type detection
  - Secure file storage with timestamped filenames
- **Course Analytics**
  - View total enrollments
  - Track course completion rates
  - Monitor student progress

### 👨‍🎓 Employee Features
- **Course Catalog**
  - Browse published courses
  - Real-time search functionality
  - Course details with lesson previews
- **Learning Experience**
  - **PDF Viewer** with page navigation and zoom controls
  - **Video Player** with standard HTML5 controls
  - **Office Document Viewer** integration
  - Mark lessons as complete/incomplete
  - Track overall course progress
  - Resume learning from last position
- **My Courses Dashboard**
  - View enrolled courses
  - Filter by status (In Progress, Completed, Not Started)
  - Progress visualization with percentage bars
  - Quick access to continue learning

### 📊 Progress Tracking
- Per-lesson completion status
- Overall course progress percentage
- Enrollment management
- Learning history

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework:** Flask (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** Flask-JWT-Extended
- **API:** RESTful architecture
- **CORS:** Flask-CORS

**Frontend:**
- **Framework:** React 18
- **Build Tool:** Vite
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Styling:** Tailwind CSS
- **PDF Viewer:** react-pdf
- **State Management:** React Context API

### Database Schema

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Companies  │──────│    Users     │──────│   Courses   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      │
                     ┌──────▼──────┐        ┌──────▼──────┐
                     │ Enrollments │        │   Lessons   │
                     └──────┬──────┘        └──────┬──────┘
                            │                      │
                            └──────────┬───────────┘
                                       │
                                ┌──────▼──────────┐
                                │ LessonProgress  │
                                └─────────────────┘
```

**Tables:**
1. **Companies** - Multi-tenant organization data
2. **Users** - User accounts with role-based permissions
3. **Courses** - Course metadata and publishing status
4. **Lessons** - Individual learning units with content
5. **Enrollments** - Student course registrations
6. **LessonProgress** - Granular completion tracking

### Multi-Tenancy

The system implements **row-level multi-tenancy** where:
- Each company's data is completely isolated
- All queries automatically filter by `company_id`
- Users can only access resources from their own company
- Enforced at both database and application levels

### API Architecture

**RESTful Endpoints:**

```
Authentication:
POST   /api/auth/register     - User registration
POST   /api/auth/login        - User login
POST   /api/auth/refresh      - Token refresh
GET    /api/auth/me           - Get current user

Courses:
GET    /api/courses           - List courses (filtered by role)
GET    /api/courses/:id       - Get course details
POST   /api/courses           - Create course (Manager/Admin)
PUT    /api/courses/:id       - Update course (Owner/Admin)
DELETE /api/courses/:id       - Delete course (Owner/Admin)
POST   /api/courses/:id/publish - Publish course

Lessons:
GET    /api/courses/:id/lessons      - List course lessons
POST   /api/courses/:id/lessons      - Create lesson
GET    /api/lessons/:id              - Get lesson details
PUT    /api/lessons/:id              - Update lesson
DELETE /api/lessons/:id              - Delete lesson
POST   /api/lessons/:id/upload       - Upload lesson content
GET    /api/lessons/:id/content      - Stream lesson content (authenticated)

Enrollments:
POST   /api/enrollments              - Enroll in course
GET    /api/enrollments/my-courses   - List user's enrollments
DELETE /api/enrollments/:id          - Unenroll from course

Progress:
POST   /api/progress/lessons/:id/complete   - Mark lesson complete
POST   /api/progress/lessons/:id/incomplete - Mark lesson incomplete
GET    /api/progress/courses/:id            - Get course progress
GET    /api/progress/my-progress            - Get all user progress
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- npm or yarn

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/skillplus.git
cd skillplus
```

**2. Backend Setup**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
flask db upgrade

# Seed initial data (optional)
python seed.py

# Run the backend server
flask run
```

The backend will run on `http://localhost:5000`

**3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost/skillplus
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:5000
```

## 📁 Project Structure

```
skillplus/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Configuration
│   │   ├── models/               # Database models
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── course.py
│   │   │   ├── lesson.py
│   │   │   ├── enrollment.py
│   │   │   └── lesson_progress.py
│   │   ├── routes/               # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── courses.py
│   │   │   ├── lessons.py
│   │   │   ├── enrollments.py
│   │   │   └── progress.py
│   │   └── utils/                # Utilities
│   │       └── decorators.py     # Auth decorators
│   ├── migrations/               # Database migrations
│   ├── uploads/                  # User-uploaded files
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── src/
    │   ├── api/                  # API client modules
    │   │   ├── axios.js          # Axios configuration
    │   │   ├── auth.js
    │   │   ├── courses.js
    │   │   ├── lessons.js
    │   │   ├── enrollments.js
    │   │   └── progress.js
    │   ├── components/
    │   │   ├── common/           # Reusable components
    │   │   │   ├── LoadingSpinner.jsx
    │   │   │   ├── ProtectedRoute.jsx
    │   │   │   ├── Toast.jsx
    │   │   │   └── PageTransition.jsx
    │   │   ├── course/
    │   │   │   └── CourseCard.jsx
    │   │   ├── layout/
    │   │   │   └── Navbar.jsx
    │   │   └── lesson/
    │   │       └── ContentViewer.jsx
    │   ├── context/              # React Context
    │   │   ├── AuthContext.jsx
    │   │   └── ToastContext.jsx
    │   ├── hooks/                # Custom hooks
    │   │   └── useAuth.js
    │   ├── pages/
    │   │   ├── auth/
    │   │   │   └── Login.jsx
    │   │   ├── student/
    │   │   │   ├── Dashboard.jsx
    │   │   │   ├── CourseCatalog.jsx
    │   │   │   ├── CourseDetail.jsx
    │   │   │   ├── LessonViewer.jsx
    │   │   │   └── MyCourses.jsx
    │   │   └── manager/
    │   │       ├── ManagerDashboard.jsx
    │   │       ├── CreateCourse.jsx
    │   │       ├── EditCourse.jsx
    │   │       └── ManageLessons.jsx
    │   ├── App.jsx               # Main app component
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## 🔒 Security Features

### Authentication
- **JWT tokens** with 1-hour expiration
- **Refresh token** mechanism
- **Password hashing** with bcrypt (cost factor: 12)
- **Token storage** in localStorage with automatic cleanup on logout

### Authorization
- **Role-based access control** enforced at API level
- **Company isolation** - Users can only access their company's data
- **Ownership checks** - Users can only modify their own resources
- **Protected routes** on frontend with automatic redirection

### File Security
- **Authenticated file serving** - All content requires valid JWT
- **Secure filenames** - Sanitization with `werkzeug.secure_filename`
- **File type validation** - Whitelist of allowed extensions
- **Path traversal prevention** - Proper path handling

### CORS Configuration
```python
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/uploads/*": {"origins": "*"}
})
```

## 🎨 UI/UX Features

- **Responsive Design** - Mobile-first approach with Tailwind CSS
- **Loading States** - Spinners and skeletons for better UX
- **Toast Notifications** - Success/error feedback
- **Page Transitions** - Smooth fade-in animations
- **Protected Routes** - Automatic redirection for unauthorized access
- **Error Handling** - User-friendly error messages

## 📊 Data Flow

### Course Creation Flow
```
Manager → Create Course Form → POST /api/courses
                               ↓
                        Course Created
                               ↓
                  Add Lessons → POST /api/courses/:id/lessons
                               ↓
                Upload Content → POST /api/lessons/:id/upload
                               ↓
                       Files stored in /uploads/
                               ↓
                  Publish Course → POST /api/courses/:id/publish
                               ↓
                    Available to Employees
```

### Learning Flow
```
Employee → Browse Catalog → View Course → Enroll
                                            ↓
                                    Start Learning
                                            ↓
                        View Lesson → GET /api/lessons/:id/content
                                            ↓
                            Stream Content (PDF/Video)
                                            ↓
                          Mark Complete → POST /api/progress/lessons/:id/complete
                                            ↓
                                Progress Updated
                                            ↓
                              Next Lesson or Certificate
```

### Authentication Flow
```
User → Login Form → POST /api/auth/login
                          ↓
              JWT Access Token + Refresh Token
                          ↓
              Stored in localStorage
                          ↓
        Axios Interceptor adds token to all requests
                          ↓
              Backend validates JWT
                          ↓
        401? → Auto-refresh or redirect to login
                          ↓
              Request succeeds
```

## 🧪 Testing

### Manual Testing
The application has been extensively tested with:
- Multiple user roles (Admin, Manager, Employee)
- Multiple companies for tenant isolation
- Various file types (PDF, video, documents)
- Edge cases (empty states, error handling)

### Test Users
```python
# Seed data provides test accounts:
Admin:    admin@techcorp.com    / adminmoe
Manager:  manager@techcorp.com  / managermoe
Employee: john@techcorp.com     / employeemoe
```

## 🔄 API Request/Response Examples

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@techcorp.com",
  "password": "employeemoe"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 3,
    "name": "John Doe",
    "email": "john@techcorp.com",
    "role": "employee",
    "company_id": 1
  }
}
```

### Create Course
```bash
POST /api/courses
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Introduction to Python",
  "description": "Learn Python programming from scratch",
  "category": "Programming"
}

Response:
{
  "message": "Course created successfully",
  "course": {
    "id": 1,
    "title": "Introduction to Python",
    "description": "Learn Python programming from scratch",
    "instructor_id": 2,
    "company_id": 1,
    "is_published": false,
    "created_at": "2024-03-25T10:30:00"
  }
}
```

### Get Course Progress
```bash
GET /api/progress/courses/1
Authorization: Bearer {token}

Response:
{
  "course": {
    "id": 1,
    "title": "Introduction to Python"
  },
  "lessons": [
    {
      "id": 1,
      "title": "Python Basics",
      "completed": true,
      "completed_at": "2024-03-20T14:30:00"
    },
    {
      "id": 2,
      "title": "Variables and Data Types",
      "completed": false,
      "completed_at": null
    }
  ],
  "progress": {
    "total_lessons": 10,
    "completed_lessons": 1,
    "percentage": 10
  }
}
```

## 🎯 Technical Highlights

### Backend Skills Demonstrated
- **RESTful API Design** - Clean, intuitive endpoint structure
- **Database Design** - Normalized schema with proper relationships
- **SQLAlchemy ORM** - Complex queries, relationships, and migrations
- **Authentication** - JWT implementation with refresh tokens
- **Authorization** - Role-based access control and ownership validation
- **Multi-tenancy** - Row-level data isolation
- **File Handling** - Upload, storage, and authenticated serving
- **Error Handling** - Comprehensive try-catch and HTTP status codes
- **Security** - Password hashing, CORS, input validation

### Frontend Skills Demonstrated
- **React Hooks** - useState, useEffect, useCallback, custom hooks
- **Context API** - Global state management (Auth, Toast)
- **React Router** - Nested routes, protected routes, navigation
- **API Integration** - Axios with interceptors for auth
- **Component Architecture** - Reusable, maintainable components
- **Responsive Design** - Tailwind CSS, mobile-first approach
- **File Upload** - FormData, progress tracking
- **PDF Rendering** - react-pdf integration
- **UX Patterns** - Loading states, error handling, toast notifications

## 🚧 Future Enhancements

- [ ] **Sections/Modules** - Group lessons into themed modules
- [ ] **Quiz System** - Multiple choice, true/false assessments
- [ ] **Certificates** - Auto-generated completion certificates
- [ ] **Discussion Forums** - Per-lesson Q&A and discussions
- [ ] **Analytics Dashboard** - Detailed progress and engagement metrics
- [ ] **Video Enhancements** - Playback speed, quality selection, chapters
- [ ] **Assignment Submissions** - File upload and grading
- [ ] **Live Sessions** - Video conferencing integration
- [ ] **Mobile Apps** - Native iOS and Android applications
- [ ] **Email Notifications** - Enrollment confirmations, reminders
- [ ] **Search** - Full-text search across courses and content
- [ ] **Gamification** - Badges, points, leaderboards

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Maurice Ngicho**
- GitHub: [@MauriceNgicho](https://github.com/MauriceNgicho)
- LinkedIn: [Maurice Ngicho](https://www.linkedin.com/in/maurice-ngicho-069654234/)
- Email: mrcngicho@gmail.com

## 🙏 Acknowledgments

- Built as a portfolio project to demonstrate full-stack development skills
- Inspired by popular LMS platforms like Moodle, Coursera, and Canvas

---

**Note:** This is an MVP (Minimum Viable Product) focused on core LMS functionality. The project demonstrates proficiency in full-stack development, database design, authentication, authorization, file handling, and modern web development practices.