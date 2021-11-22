from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student, Teacher, Course, EnrolledCourses, CoursesTaught, Quiz, Question, Answer, Grade

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(EnrolledCourses)
admin.site.register(CoursesTaught)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Grade)
