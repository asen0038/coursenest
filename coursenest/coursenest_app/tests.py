from django.test import TestCase
from django.test import Client, RequestFactory
from django.urls import reverse

from .models import *
from django.contrib.auth import authenticate, login, logout
from .views import *


class CoursenestTestClass(TestCase):

    # Testing the feature where a student user is created
    def test_student_model(self):

        user = User.objects.create_user(username="student", password="student")
        self.assertIsNotNone(user)

        student = Student.objects.get(user=user)
        self.assertIsNotNone(student)
        self.assertEqual(student.__str__(), "student")
        self.assertEqual(student.overall_grade, 0)

        student.overall_grade = 32
        student.save()
        stu = Student.objects.get(user=user)
        self.assertEqual(stu.overall_grade, 32)

    # Testing the feature where a teacher user is created
    def test_teacher_model(self):

        user = User.objects.create_user(username="teacher", password="teacher")
        self.assertIsNotNone(user)

        teacher = Teacher.objects.get(user=user)
        self.assertIsNotNone(teacher)
        self.assertEqual(teacher.__str__(), "teacher")
        self.assertEqual(teacher.university, "")

        teacher.university = "USYD"
        teacher.save()
        tea = Teacher.objects.get(user=user)
        self.assertEqual(tea.university, "USYD")

    # Testing the welcome screen view
    def test_welcome_view(self):
        response = Client().get("/coursenest_app/")
        self.assertEqual(response.status_code, 200)

        client = Client()
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()

        client.force_login(user=u)
        res = client.get("/coursenest_app/")
        self.assertEqual(res.status_code, 200)

    # Testing the student dashboard get view
    def test_studentdash_view(self):

        client = Client()
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()
        student = Student.objects.get(user=u)

        client.force_login(user=u)
        response = client.get(reverse('coursenest_app:studentdash', kwargs={'id': student.id}))
        self.assertEqual(response.status_code, 200)

        u1 = User.objects.create_user(username="teacher", password="elec3609")
        u1.save()
        teacher = Teacher.objects.get(user=u1)
        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)

        res = client.post(reverse('coursenest_app:studentdash', kwargs={'id': student.id}), {'cid': course.id})
        self.assertEqual(res.status_code, 200)

        res2 = client.post(reverse('coursenest_app:coursedetail', kwargs={'id': course.id}))
        self.assertEqual(res2.status_code, 200)

    # Testing the student enroll list get/post view
    def test_student_enrollist_view(self):

        client = Client()
        res = client.get(reverse('coursenest_app:courselist')) #Not logined
        self.assertEqual(res.status_code, 302)
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()
        student = Student.objects.get(user=u)

        client.force_login(user=u)
        response = client.get(reverse("coursenest_app:courselist"))
        self.assertEqual(response.status_code, 200)

        u1 = User.objects.create_user(username="teacher", password="elec3609")
        u1.save()
        teacher = Teacher.objects.get(user=u1)
        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        self.assertEqual(course.__str__(), "TEST")
        quiz = Quiz.objects.create(name="test quiz", course=course)
        self.assertEqual(quiz.__str__(), "test quiz")
        question = Question.objects.create(question="What is this?", quiz=quiz)
        self.assertEqual(question.__str__(), "What is this?")
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        self.assertEqual(answer.__str__(), "This is this")
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)
        self.assertEqual(grade.__str__(), 0)

        response = client.post(reverse('coursenest_app:courselist'), {'cid': course.id})
        self.assertEqual(response.status_code, 200)

    def test_login_student(self):

        client = Client()
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()

        response = client.post(reverse('coursenest_app:loginStudent'), {'username': 'teacher', 'password': 'elec3609'})
        self.assertEqual(response.status_code, 200)

        response = client.post(reverse('coursenest_app:loginStudent'), {'username': 'student', 'password': 'elec3609'})
        self.assertEqual(response.status_code, 302)

    def test_login_teacher(self):

        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()

        response = client.post(reverse('coursenest_app:loginTeacher'), {'username': 'student', 'password': 'elec3609'})
        self.assertEqual(response.status_code, 200)

        response = client.post(reverse('coursenest_app:loginTeacher'), {'username': 'teacher', 'password': 'elec3609'})
        self.assertEqual(response.status_code, 302)


    def test_student_register(self):

        client = Client()

        response = client.post(reverse('coursenest_app:registerStudent'), {'username': 'student', 'password1': 'elec3609'})
        self.assertEqual(response.status_code, 200)

        data = {'username': 'student',
                   'first_name': 'testfirst',
                   'last_name': 'testlast',
                   'email': 'test@gmail.com',
                   'password1': 'elec3609',
                   'password2': 'elec3609'}

        response = client.post(reverse('coursenest_app:registerStudent'), data)
        self.assertEqual(response.status_code, 302)

    def test_teacher_register(self):

        client = Client()

        response = client.post(reverse('coursenest_app:registerTeacher'), {'username': 'teacher', 'password1': 'elec3609'})
        self.assertEqual(response.status_code, 200)

        data = {'username': 'teacher',
                   'first_name': 'testfirst',
                   'last_name': 'testlast',
                   'email': 'test@gmail.com',
                   'password1': 'elec3609',
                   'password2': 'elec3609'}

        response = client.post(reverse('coursenest_app:registerTeacher'), data)
        self.assertEqual(response.status_code, 302)

    def test_student_profile(self):

        client = Client()
        res = client.get(reverse('coursenest_app:studentpro', kwargs={'id': 1}))  # Not logined
        self.assertEqual(res.status_code, 302)
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()
        student = Student.objects.get(user=u)

        u1 = User.objects.create_user(username="teacher", password="elec3609")
        u1.save()
        teacher = Teacher.objects.get(user=u1)
        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)

        client.force_login(user=u)
        response = client.get(reverse('coursenest_app:studentpro', kwargs={'id': student.id}))
        self.assertEqual(response.status_code, 200)

        enpair = EnrolledCourses.objects.create(course=course, student=student)
        response = client.get(reverse('coursenest_app:studentpro', kwargs={'id': student.id}))
        self.assertEqual(response.status_code, 200)

        data = {'university': 'USYD',
                'degree': 'eng'}

        response = client.post(reverse('coursenest_app:studentpro', kwargs={'id': student.id}), data)
        self.assertEqual(response.status_code, 200)

    def test_teacher_profile(self):

        client = Client()
        res = client.get(reverse('coursenest_app:teacherpro', kwargs={'id': 1}))  # Not logined
        self.assertEqual(res.status_code, 302)
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        teacher = Teacher.objects.get(user=u)

        client.force_login(user=u)
        response = client.get(reverse('coursenest_app:teacherpro', kwargs={'id': teacher.id}))
        self.assertEqual(response.status_code, 200)

        data = {'university': 'USYD',
                'department': 'eng'}

        response = client.post(reverse('coursenest_app:teacherpro', kwargs={'id': teacher.id}), data)
        self.assertEqual(response.status_code, 200)

    def test_teacherdash_view(self):

        client = Client()
        res = client.get(reverse('coursenest_app:teacherdash', kwargs={'id': 1}))  # Not logined
        self.assertEqual(res.status_code, 302)

        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        teacher = Teacher.objects.get(user=u)
        client.force_login(user=u)
        res = client.get(reverse('coursenest_app:teacherdash', kwargs={'id': teacher.id}))
        self.assertEqual(res.status_code, 200)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)
        enpair = EnrolledCourses.objects.create(course=course, student=student)

        res = client.post(reverse('coursenest_app:teacherdash', kwargs={'id': teacher.id}), {'cid': course.id})
        self.assertEqual(res.status_code, 200)

    def test_coursedetail_edit(self):

        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        teacher = Teacher.objects.get(user=u)
        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)

        client.force_login(user=u)
        res = client.get(reverse('coursenest_app:coursedetailedit', kwargs={'id': course.id}))
        self.assertEqual(res.status_code, 200)

        data = {'code': 'TEST',
                'name': 'testing',
                'description': 'testing'}
        res = client.post(reverse('coursenest_app:coursedetailedit', kwargs={'id': course.id}), data)
        self.assertEqual(res.status_code, 200)

    def test_gradlist_view(self):
        client = Client()
        u = User.objects.create_user(username="student", password="elec3609")
        u.save()
        student = Student.objects.get(user=u)

        client.force_login(user=u)

        u1 = User.objects.create_user(username="teacher", password="elec3609")
        u1.save()
        teacher = Teacher.objects.get(user=u1)
        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)

        response = client.get(reverse('coursenest_app:gradelist'))
        self.assertEqual(response.status_code, 200)

    def test_createcourse(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        data = {'code': 'TEST1234',
                'name': 'Test',
                'description': 'testing'}
        res = client.post(reverse('coursenest_app:createcourse'), data)
        self.assertEqual(res.status_code, 200)

        res = client.get(reverse('coursenest_app:createcourse'))
        self.assertEqual(res.status_code, 200)

    def test_studentlist_view(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)

        data = {f'mark{student.id}': '90'}
        res = client.post(reverse('coursenest_app:studentlist', kwargs={'id': course.id}), data)
        self.assertEqual(res.status_code, 200)

        res = client.get(reverse('coursenest_app:studentlist', kwargs={'id': course.id}))
        self.assertEqual(res.status_code, 200)

    def test_managequiz(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        grade = Grade.objects.create(student=student, course=course, quiz=quiz)

        data = {'cid': question.id}
        res = client.post(reverse('coursenest_app:managequiz', kwargs={'id': course.id}), data)
        self.assertEqual(res.status_code, 200)

    def test_quizzes_view(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer1 = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        answer2 = Answer.objects.create(question=question, answer="This is that", isCorrect=False)
        answer3 = Answer.objects.create(question=question, answer="This is Sparta", isCorrect=True)
        answer4 = Answer.objects.create(question=question, answer="This is", isCorrect=False)
        grade1 = Grade.objects.create(mark=75, student=student, course=course, quiz=quiz)
        grade2 = Grade.objects.create(mark=50, student=student, course=course, quiz=quiz)
        grade3 = Grade.objects.create(mark=25, student=student, course=course, quiz=quiz)
        grade4 = Grade.objects.create(mark=100, student=student, course=course, quiz=quiz)

        res = client.get(reverse('coursenest_app:quizzes', kwargs={'id': course.id}))
        self.assertEqual(res.status_code, 200)

    def test_createquestion(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)

        res = client.get(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}))
        self.assertEqual(res.status_code, 200)

        data = {'question_text': '',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4',
                'answer': 'A'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4',
                'answer': 'A'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '',
                'answerC': '3',
                'answerD': '4',
                'answer': 'A'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '',
                'answerD': '4',
                'answer': 'A'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '',
                'answer': 'A'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4'}
        res = client.post(reverse('coursenest_app:createquestion', kwargs={'id': quiz.id}), data)
        self.assertEqual(res.status_code, 302)

    def test_editquestion(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer1 = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        answer2 = Answer.objects.create(question=question, answer="This is that", isCorrect=False)
        answer3 = Answer.objects.create(question=question, answer="This is Sparta", isCorrect=True)
        answer4 = Answer.objects.create(question=question, answer="This is", isCorrect=False)

        res = client.get(reverse('coursenest_app:editquestion', kwargs={'id': question.id}))
        self.assertEqual(res.status_code, 200)

        data = {'question_text': '',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '',
                'answerC': '3',
                'answerD': '4',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '',
                'answerD': '4',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

        data = {'question_text': 'What time is it?',
                'answerA': '1',
                'answerB': '2',
                'answerC': '3',
                'answerD': '4',
                'answer': 'C'}
        res = client.post(reverse('coursenest_app:editquestion', kwargs={'id': question.id}), data)
        self.assertEqual(res.status_code, 200)

    def test_takequiz(self):
        client = Client()
        u = User.objects.create_user(username="teacher", password="elec3609")
        u.save()
        client.force_login(user=u)
        teacher = Teacher.objects.get(user=u)

        u1 = User.objects.create_user(username="student", password="elec3609")
        u1.save()
        student = Student.objects.get(user=u1)

        course = Course.objects.create(code="TEST", name="testing", description="testing", teacher=teacher)
        pair = CoursesTaught.objects.create(course=course, teacher=teacher)
        enpair = EnrolledCourses.objects.create(course=course, student=student)
        quiz = Quiz.objects.create(name="test quiz", course=course)
        question = Question.objects.create(question="What is this?", quiz=quiz)
        answer1 = Answer.objects.create(question=question, answer="This is this", isCorrect=False)
        answer2 = Answer.objects.create(question=question, answer="This is that", isCorrect=False)
        answer3 = Answer.objects.create(question=question, answer="This is Sparta", isCorrect=True)
        answer4 = Answer.objects.create(question=question, answer="This is", isCorrect=False)

        res = client.get(reverse('coursenest_app:takequiz', kwargs={'id': course.id}))
        self.assertEqual(res.status_code, 200)

        data = {f'question{question.id}': 'C'}
        res = client.post(reverse('coursenest_app:takequiz', kwargs={'id': course.id}), data)
        self.assertEqual(res.status_code, 302)

        data = {f'question{question.id}': 'A'}
        res = client.post(reverse('coursenest_app:takequiz', kwargs={'id': course.id}), data)
        self.assertEqual(res.status_code, 302)

