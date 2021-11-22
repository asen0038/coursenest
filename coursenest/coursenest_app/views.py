from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, Http404
from django.http.response import HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import CourseForm

from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
from .serializers import CourseSerializer

from coursenest_app.forms import Register

# TODO: get all print() statements to instead return a 400 or 404 http response
from coursenest_app.models import Student, Teacher


def welcome(request):
    if request.user.is_authenticated:        
        request.session.clear()
        logout(request)
    return render(request, 'coursenest_app/welcome.html')


def registerStudent(request):
    form = Register(request.POST)
    error = ""
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        teacher = get_object_or_404(Teacher, user=user)  # Duplication of a user trying to be both
        teacher.delete()
        student = get_object_or_404(Student, user=user)
        return redirect("studentdash/{}".format(student.id))  # TODO: redirect to student dashboard using 'student'
    else:
        form = Register()
        error = form.errors
    return render(request, 'coursenest_app/register.html', {'form': form, "error": error})


def loginStudent(request):
    error = ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                student = get_object_or_404(Student, user=user)  # only student can login here
                if student is not None:
                    login(request, user)
                    print(request, f"You are now logged in as {username}.")
                    return redirect("studentdash/{}".format(student.id))  # TODO: redirect to student dashboard using 'student'
                else:
                    print(request, "Invalid username or password.") 
                    error = "Invalid username or password."
            else:
                print(request, "Invalid username or password.")
                error = "Invalid username or password."
        else:
            print(request, "Invalid username or password.")
            error = "Invalid username or password."

    form = AuthenticationForm()
    return render(request, 'coursenest_app/login.html', {'form': form, "error": error})


def registerTeacher(request):
    error = ""
    form = Register(request.POST)
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        student = get_object_or_404(Student, user=user)  # Duplication of a user trying to be both
        student.delete()
        teacher = get_object_or_404(Teacher, user=user)
        return redirect("teacherdash/{}".format(teacher.id))
    else:
        form = Register()
        error = form.errors
    return render(request, 'coursenest_app/register.html', {'form': form, "error": error})


def loginTeacher(request):
    error = ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                teacher = get_object_or_404(Teacher, user=user)  # only student can login here
                if teacher is not None:
                    login(request, user)
                    print(request, f"You are now logged in as {username}.")
                    return redirect("teacherdash/{}".format(teacher.id))
                else:
                    print(request, "Invalid username or password.")
                    error = "Invalid username or password."
            else:
                print(request, "Invalid username or password.")
                error = "Invalid username or password."
        else:
            print(request, "Invalid username or password.")
            error = "Invalid username or password."
    form = AuthenticationForm()
    return render(request, 'coursenest_app/login.html', {'form': form, "error": error})


def coursedetail(request, id):
    if request.user.is_authenticated:
        # save post data
        myUser = request.user
        student = get_object_or_404(Student, user=myUser)
        course = get_object_or_404(Course, id=id)
        teacherUser = get_object_or_404(User, teacher=course.teacher)

        return render(request, 'coursenest_app/studentcoursedetail.html',
                    {"id": student.id, "course": course, "teacher": teacherUser})
    else:
        return HttpResponseServerError('Not Login')  # not login


def studentdash(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        student = get_object_or_404(Student, user=myUser)
        if request.method == "POST":
            c = request.POST.get('cid')
            course = get_object_or_404(Course, id=c)
            enpair = get_object_or_404(EnrolledCourses, course=course, student=student)
            quiz = get_object_or_404(Quiz, course=course)
            grade = get_object_or_404(Grade, course=course, quiz=quiz, student=student)
            grade.delete()
            enpair.delete()

        courses = EnrolledCourses.objects.filter(student=student)

        return render(request, 'coursenest_app/studentdash.html', {'course': courses, 'id': student.id})
    else:
        return redirect('/coursenest_app/')  # not login


def studentpro(request, id):
    if request.user.is_authenticated:
        # if has login
        myUser = request.user
        student = get_object_or_404(Student, id=id)
        grades = Grade.objects.filter(student=student)
        encourses = EnrolledCourses.objects.filter(student=student)
        overall_grades = 0
        for grade in grades:
            overall_grades += int(grade.mark)
        if len(encourses) < 1:
            student.overall_grade = 0
        else:
            student.overall_grade = int(overall_grades / len(encourses))
        student.save()
        if request.POST:
            # save post data
            student.university = request.POST.get('university')
            student.degree = request.POST.get('degree')
            desc = request.POST.get('description')
            if desc == None:
                desc = ""
            student.description = desc
            student.save()
        return render(request, 'coursenest_app/studentpro.html',
                      {"id": student.id, "student": student, "user": myUser, "overall_grades": overall_grades})
    else:
        return redirect('/coursenest_app/')  # not login


def enrollList(request):
    if request.user.is_authenticated:

        myUser = request.user
        student = get_object_or_404(Student, user=myUser)

        if request.method == "POST":
            c = request.POST.get('cid')
            course = get_object_or_404(Course, id=c)
            quiz = get_object_or_404(Quiz, course=course)
            is_paired = EnrolledCourses.objects.filter(student=student, course=course)
            if len(is_paired) < 1:
                pair = EnrolledCourses(student=student, course=course)
                pair.save()
                grade = Grade(quiz=quiz, student=student, course=course)
                grade.save()

        studentcourses = EnrolledCourses.objects.filter(student=student)
        allcourses = Course.objects.all()
        for i in studentcourses:
            allcourses = allcourses.exclude(id=i.course.id)

        return render(request, 'coursenest_app/courselist.html', {"id": student.id, "courses": allcourses, })
    else:
        return redirect('/coursenest_app/')  # not login


def teacherdash(request, id):
    if request.user.is_authenticated:
        teacher = get_object_or_404(Teacher, id=id)
        if request.method == "POST":
            c = request.POST.get('cid')
            course = get_object_or_404(Course, id=c)
            coursetaught = get_object_or_404(CoursesTaught, course=course, teacher=teacher)
            coursetaught.delete()
            quiz = get_object_or_404(Quiz, course=course)
            questions = Question.objects.filter(quiz=quiz)
            for qu in questions:
                answers = Answer.objects.filter(question=qu)
                answers.delete()
            questions.delete()
            grades = Grade.objects.filter(course=course, quiz=quiz)
            grades.delete()
            enrolled = EnrolledCourses.objects.filter(course=course)
            enrolled.delete()
            quiz.delete()
            course.delete()

        courses = CoursesTaught.objects.filter(teacher=teacher)

        return render(request, 'coursenest_app/teacherdash.html', {'course': courses, 'id': teacher.id})
    else:
        return redirect('/coursenest_app/')  # not login


def managequiz(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        if request.method == "POST":
            c = request.POST.get('cid')
            question = get_object_or_404(Question, id=c)
            answers = Answer.objects.filter(question=question)
            answers.delete()
            question.delete()

        quiz = get_object_or_404(Quiz, course_id=id)
        course = get_object_or_404(Course, id=id)
        questions = Question.objects.filter(quiz_id=quiz.id).order_by('id')

        return render(request, 'coursenest_app/managequiz.html', {'quiz': quiz, 'questions': questions, 'id': teacher.id,
                                                                'course': course})
    else:
        return redirect('/coursenest_app/')  # not login


def quizzes(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        cucourse = Course.objects.get(id=id)
        cuquiz = Quiz.objects.get(course=cucourse)
        grade = list(Grade.objects.filter(course=cucourse, quiz=cuquiz))
        high_grade = 0
        mean_grade = 0
        low_grade = 0
        grade_count = len(grade)
        if grade_count > 0:
            low_grade = grade[0].mark
        for i in range(0, grade_count):
            if high_grade < grade[i].mark:
                high_grade = grade[i].mark
            elif low_grade > grade[i].mark:
                low_grade = grade[i].mark
            mean_grade += grade[i].mark
        if grade_count > 0:
            mean_grade = int(mean_grade / grade_count)
        cuquestions = list(Question.objects.filter(quiz=cuquiz).order_by('id'))
        answers = []
        answers_zip = []
        canswers = []
        anLabels = ["A", "B", "C", "D"]
        for cu in cuquestions:
            answer = list(Answer.objects.filter(question=cu))
            tempc = ""
            for i in range(0, 4):
                if answer[i].isCorrect is True:
                    tempc = str(chr(ord('A') + i))
                    break
            canswers.append(tempc)
            answers.append(answer)
            answers_zip.append(zip(anLabels, answer))
        zipData = zip(cuquestions, answers_zip, canswers)
        return render(request, 'coursenest_app/quizzes.html', {"zipData": zipData, "id": teacher.id, "course": cucourse
            , "high_grade": high_grade, "low_grade": low_grade, "mean_grade": mean_grade})
    else:
        return redirect('/coursenest_app/')  # not login


def teacherpro(request, id):
    if request.user.is_authenticated:
        # if has login
        myUser = request.user
        teacher = get_object_or_404(Teacher, id=id)
        if request.POST:
            # save post data
            teacher.university = request.POST.get('university')
            teacher.department = request.POST.get('department')
            desc = request.POST.get('description')
            if desc == None:
                desc = ""
            teacher.description = desc
            teacher.save()
        return render(request, 'coursenest_app/teacherpro.html',
                      {"id": teacher.id, "teacher": teacher, "user": myUser, })
    else:
        return redirect('/coursenest_app/')  # not login


def coursedetailedit(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        course = get_object_or_404(Course, id=id)
        enrolled_count = len(EnrolledCourses.objects.filter(course_id=id))

        if request.POST:
            course.code = request.POST.get('code')
            course.name = request.POST.get('name')
            course.description = request.POST.get('description')
            course.save()

        return render(request, 'coursenest_app/coursedetailedit.html',
                    {"id": teacher.id, "course": course, "enrolled_count": enrolled_count})
    else:
        return redirect('/coursenest_app/')  # not login

def studentlist(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        course = get_object_or_404(Course, id=id)
        quiz = get_object_or_404(Quiz, course=course)
        if request.method == "POST":
            enroll_list = list(EnrolledCourses.objects.filter(course=course))
            students = []
            for enroll in enroll_list:
                student = get_object_or_404(Student, id=enroll.student_id)
                students.append(student)
            for student in students:
                mark = int(request.POST.get("mark" + str(student.id)))
                print(mark)
                mgrade = get_object_or_404(Grade, quiz=quiz, course=course, student=student)
                mgrade.mark = mark
                mgrade.save()
            print("saved!")

        enroll_list = list(EnrolledCourses.objects.filter(course=course))
        grades = []
        students = []
        for enroll in enroll_list:
            student = get_object_or_404(Student, id=enroll.student_id)
            grade = get_object_or_404(Grade, quiz=quiz, course=course, student=student)
            grades.append(grade)
            students.append(student)
        zipData = zip(students, grades)
        return render(request, 'coursenest_app/studentlist.html',
                    {"id": teacher.id, "zipData": zipData, "course": course})
    else:
        return redirect('/coursenest_app/')  # not login


def createcourse(request):
    if request.user.is_authenticated:
        context = {}
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)

        form = CourseForm(request.POST or None)
        if form.is_valid():
            form.instance.teacher = teacher
            form.save()
            course = form.instance
            pair = CoursesTaught(teacher=teacher, course=course)
            pair.save()
            quiz = Quiz(name=course.code, course=course)
            quiz.save()

        context['id'] = teacher.id
        context['form'] = form
        return render(request, "coursenest_app/createcourse.html", context)
    else:
        return redirect('/coursenest_app/')  # not login


def createquestion(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        quiz = get_object_or_404(Quiz, id=id)

        context = {}
        error_text = ""
        question_text = ""
        answerA = ""
        answerB = ""
        answerC = ""
        answerD = ""
        answer = ""

        if request.method == "POST":
            question_text = request.POST.get("question_text")
            answerA = request.POST.get("answerA")
            answerB = request.POST.get("answerB")
            answerC = request.POST.get("answerC")
            answerD = request.POST.get("answerD")
            answer = str(request.POST.get("answer"))
            print(answer)
            if question_text == "":
                error_text = "Input the Question Text!"
            elif answerA == "":
                error_text = "Input the text of Answer A!"
            elif answerB == "":
                error_text = "Input the text of Answer B!"
            elif answerC == "":
                error_text = "Input the text of Answer C!"
            elif answerD == "":
                error_text = "Input the text of Answer D!"
            elif answer is None:
                error_text = "Select the correct answer!"
            else:
                question = Question(question=question_text, quiz=quiz)
                question.save()
                temp = answer == "A"
                an = Answer(question=question, answer=answerA, isCorrect=temp)
                an.save()
                temp = answer == "B"
                an = Answer(question=question, answer=answerB, isCorrect=temp)
                an.save()
                temp = answer == "C"
                an = Answer(question=question, answer=answerC, isCorrect=temp)
                an.save()
                temp = answer == "D"
                an = Answer(question=question, answer=answerD, isCorrect=temp)
                an.save()
                return redirect("coursenest_app:managequiz", id=quiz.course_id)

        context['error'] = error_text
        context['question_text'] = question_text
        context['answerA'] = answerA
        context['answerB'] = answerB
        context['answerC'] = answerC
        context['answerD'] = answerD
        context['answer'] = answer
        context['id'] = teacher.id
        context['quiz'] = quiz
        return render(request, "coursenest_app/createquestion.html", context)
    else:
        return redirect('/coursenest_app/')  # not login


def editquestion(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        teacher = get_object_or_404(Teacher, user=myUser)
        question = get_object_or_404(Question, id=id)
        answers = list(Answer.objects.filter(question_id=question.id))
        quiz = get_object_or_404(Quiz, id=question.quiz_id)

        context = {}
        error_text = ""
        question_text = question.question
        answerA = answers[0].answer
        answerB = answers[1].answer
        answerC = answers[2].answer
        answerD = answers[3].answer
        answer = ""
        for i in range(0, len(answers)):
            print(answers[i].isCorrect)
            if answers[i].isCorrect is True:
                answer += chr(ord('A') + i)
                break
        print(answer)

        if request.method == "POST":
            question_text = request.POST.get("question_text")
            answerA = request.POST.get("answerA")
            answerB = request.POST.get("answerB")
            answerC = request.POST.get("answerC")
            answerD = request.POST.get("answerD")
            answer = request.POST.get("answer")
            print(answer)
            if question_text == "":
                error_text = "Input the Question Text!"
            elif answerA == "":
                error_text = "Input the text of Answer A!"
            elif answerB == "":
                error_text = "Input the text of Answer B!"
            elif answerC == "":
                error_text = "Input the text of Answer C!"
            elif answerD == "":
                error_text = "Input the text of Answer D!"
            elif answer is None:
                error_text = "Select the correct answer!"
            else:
                question.question = question_text
                question.save()
                answers[0].answer = answerA
                answers[0].isCorrect = (answer == 'A')
                answers[0].save()
                answers[1].answer = answerB
                answers[1].isCorrect = (answer == 'B')
                answers[1].save()
                answers[2].answer = answerC
                answers[2].isCorrect = (answer == 'C')
                answers[2].save()
                answers[3].answer = answerD
                answers[3].isCorrect = (answer == 'D')
                answers[3].save()

        context['error'] = error_text
        context['question_text'] = question_text
        context['answerA'] = answerA
        context['answerB'] = answerB
        context['answerC'] = answerC
        context['answerD'] = answerD
        context['answer'] = answer
        context['id'] = teacher.id
        context['quiz'] = quiz
        return render(request, "coursenest_app/editquestion.html", context)
    else:
        return redirect('/coursenest_app/')  # not login



def takequiz(request, id):
    if request.user.is_authenticated:
        myUser = request.user
        student = get_object_or_404(Student, user=myUser)
        cucourse = Course.objects.get(id=id)
        cuquiz = Quiz.objects.get(course=cucourse)
        cuquestions = list(Question.objects.filter(quiz=cuquiz).order_by('id'))
        answers = []
        answers_zip = []
        anLabels = ["A", "B", "C", "D"]
        for cu in cuquestions:
            answer = list(Answer.objects.filter(question=cu))
            answers.append(answer)
            answers_zip.append(zip(anLabels, answer))
        zipData = zip(cuquestions, answers_zip)
        if request.method == "POST":
            score = 100
            if len(cuquestions) == 0:
                score = 0
            else:
                unit_score = int(100 / len(cuquestions))

                for question, answer in zip(cuquestions, answers):
                    question_answer = request.POST.get("question" + str(question.id))
                    if question_answer is None:
                        score -= unit_score
                    else:
                        print(question_answer)
                        temp = ord(question_answer) - ord('A')
                        print(temp)
                        if 0 <= temp < 4:
                            if answer[temp].isCorrect is False:
                                score -= unit_score
                        else:
                            score -= unit_score

            grade = Grade.objects.filter(course=cucourse, quiz=cuquiz, student=student)
            if len(grade) < 1:
                grade = Grade(mark=score, course=cucourse, quiz=cuquiz, student=student)
                grade.save()
            else:
                grade[0].mark = score
                grade[0].save()
            return redirect('coursenest_app:studentdash', id=student.id)
        return render(request, 'coursenest_app/takequiz.html', {"zipData": zipData, "id": student.id, "course": cucourse})
    else:
        return HttpResponseServerError('Not Login')  # not login


def gradelist(request):
    if request.user.is_authenticated:
        myUser = request.user
        student = get_object_or_404(Student, user=myUser)
        course_list = list(EnrolledCourses.objects.filter(student=student))
        print(course_list)
        grades = []
        course_ls = []
        for course in course_list:
            quiz = get_object_or_404(Quiz, course_id=course.course_id)
            course_ls.append(get_object_or_404(Course, id=course.course_id))
            grade = get_object_or_404(Grade, quiz=quiz, course_id=course.course_id, student=student)
            grades.append(grade)
        courses = zip(course_ls, grades)
        return render(request, 'coursenest_app/gradelist.html', {"courses": courses, "id": student.id})
    else:
        return redirect('/coursenest_app/')  # not login


# REST API for Course Model (CRUD) #


class ListAPI(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CreateAPI(CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class UpdateAPI(UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class DeleteAPI(DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
