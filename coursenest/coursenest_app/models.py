from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, default='')
    university = models.CharField(max_length=500, blank=True)
    degree = models.CharField(max_length=200, blank=True)
    overall_grade = models.IntegerField(default=0)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, default='')
    university = models.CharField(max_length=500, blank=True)
    department = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username


def create_student(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = Student.objects.create(user=user)
        user_profile.save()


post_save.connect(create_student, sender=User)


def create_teacher(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = Teacher.objects.create(user=user)
        user_profile.save()


post_save.connect(create_teacher, sender=User)


class Course(models.Model):
    code = models.CharField(max_length=500, unique=True)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.code


class EnrolledCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class CoursesTaught(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Quiz(models.Model):
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.CharField(max_length=1000)
    quiz = models.ForeignKey(Quiz, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.question


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    answer = models.CharField(max_length=1000)
    isCorrect = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class Grade(models.Model):
    mark = models.IntegerField(default=0)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    quiz = models.ForeignKey(Quiz, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.mark

