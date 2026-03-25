from app import create_app, db
from app.models.company import Company
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress
from datetime import datetime

def seed_database():
    """Seed the database with test data."""
    
    app = create_app('development')
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        LessonProgress.query.delete()
        Enrollment.query.delete()
        Lesson.query.delete()
        Course.query.delete()
        User.query.delete()
        Company.query.delete()
        db.session.commit()
        
        # Create companies
        print("Creating companies...")
        company1 = Company(
            name='TechCorp Solutions',
            subdomain='techcorp',
            subscription_plan='pro',
            max_users=100
        )
        company2 = Company(
            name='StartupHub Inc',
            subdomain='startuphub',
            subscription_plan='basic',
            max_users=50
        )
        db.session.add_all([company1, company2])
        db.session.commit()
        
        # Create users
        print("Creating users...")
        admin1 = User(company_id=company1.id, email='admin@techcorp.com', 
                     first_name='Alice', last_name='Admin', role='admin')
        admin1.set_password('adminmoe')
        
        manager1 = User(company_id=company1.id, email='manager@techcorp.com',
                       first_name='Mike', last_name='Manager', role='manager')
        manager1.set_password('managermoe')
        
        employee1 = User(company_id=company1.id, email='john@techcorp.com',
                        first_name='John', last_name='Doe', role='employee')
        employee1.set_password('employeemoe')
        
        employee2 = User(company_id=company1.id, email='jane@techcorp.com',
                        first_name='Jane', last_name='Smith', role='employee')
        employee2.set_password('employeemoe')
        
        admin2 = User(company_id=company2.id, email='admin@startuphub.com',
                     first_name='Sarah', last_name='Director', role='admin')
        admin2.set_password('adminmoe')
        
        employee3 = User(company_id=company2.id, email='bob@startuphub.com',
                        first_name='Bob', last_name='Johnson', role='employee')
        employee3.set_password('employeemoe')
        
        db.session.add_all([admin1, manager1, employee1, employee2, admin2, employee3])
        db.session.commit()
        
        # Create courses
        print("Creating courses...")
        course1 = Course(company_id=company1.id, instructor_id=manager1.id,
                        title='Python Programming Basics',
                        description='Learn Python from scratch', is_published=True)
        
        course2 = Course(company_id=company1.id, instructor_id=manager1.id,
                        title='Data Analysis with Pandas',
                        description='Master Pandas library', is_published=True)
        
        course3 = Course(company_id=company1.id, instructor_id=manager1.id,
                        title='Machine Learning 101',
                        description='ML fundamentals', is_published=False)
        
        course4 = Course(company_id=company2.id, instructor_id=admin2.id,
                        title='Startup Growth Strategies',
                        description='Scale your startup', is_published=True)
        
        db.session.add_all([course1, course2, course3, course4])
        db.session.commit()
        
        # Create lessons
        print("Creating lessons...")
        lessons_c1 = [
            Lesson(course_id=course1.id, title='Introduction to Python', 
                   content_type='video', order_index=1, duration_minutes=15),
            Lesson(course_id=course1.id, title='Variables and Data Types',
                   content_type='video', order_index=2, duration_minutes=20),
            Lesson(course_id=course1.id, title='Control Flow',
                   content_type='video', order_index=3, duration_minutes=25),
            Lesson(course_id=course1.id, title='Practice Exercises',
                   content_type='document', order_index=4, duration_minutes=30),
        ]
        
        lessons_c2 = [
            Lesson(course_id=course2.id, title='Introduction to Pandas',
                   content_type='video', order_index=1, duration_minutes=10),
            Lesson(course_id=course2.id, title='Working with DataFrames',
                   content_type='video', order_index=2, duration_minutes=30),
            Lesson(course_id=course2.id, title='Data Cleaning',
                   content_type='video', order_index=3, duration_minutes=25),
        ]
        
        lessons_c4 = [
            Lesson(course_id=course4.id, title='Product-Market Fit',
                   content_type='video', order_index=1, duration_minutes=20),
            Lesson(course_id=course4.id, title='Fundraising Basics',
                   content_type='document', order_index=2, duration_minutes=40),
        ]
        
        db.session.add_all(lessons_c1 + lessons_c2 + lessons_c4)
        db.session.commit()
        
        # Create enrollments
        print("Creating enrollments...")
        enrollments = [
            Enrollment(user_id=employee1.id, course_id=course1.id, status='in_progress'),
            Enrollment(user_id=employee1.id, course_id=course2.id, status='enrolled'),
            Enrollment(user_id=employee2.id, course_id=course1.id, status='enrolled'),
            Enrollment(user_id=employee3.id, course_id=course4.id, status='in_progress'),
        ]
        db.session.add_all(enrollments)
        db.session.commit()
        
        # Create progress records
        print("Creating lesson progress...")
        progress = [
            LessonProgress(user_id=employee1.id, lesson_id=lessons_c1[0].id,
                          completed=True, completed_at=datetime.utcnow()),
            LessonProgress(user_id=employee1.id, lesson_id=lessons_c1[1].id,
                          completed=True, completed_at=datetime.utcnow()),
            LessonProgress(user_id=employee1.id, lesson_id=lessons_c1[2].id,
                          completed=False),
            LessonProgress(user_id=employee3.id, lesson_id=lessons_c4[0].id,
                          completed=True, completed_at=datetime.utcnow()),
        ]
        db.session.add_all(progress)
        db.session.commit()
        
        print("\n Seed data created successfully!")
        print(f" Summary:")
        print(f"   Companies: {Company.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Courses: {Course.query.count()}")
        print(f"   Lessons: {Lesson.query.count()}")
        print(f"   Enrollments: {Enrollment.query.count()}")
        print(f"   Progress Records: {LessonProgress.query.count()}")

if __name__ == '__main__':
    seed_database()