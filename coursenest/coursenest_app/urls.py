from django.urls import path

from . import views

app_name = 'coursenest_app'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register_student', views.registerStudent, name='registerStudent'),
    path('login_student', views.loginStudent, name='loginStudent'),
    path('register_teacher', views.registerTeacher, name='registerTeacher'),
    path('login_teacher', views.loginTeacher, name='loginTeacher'),
    path('studentdash/<id>', views.studentdash, name='studentdash'),
    path('studentpro/<id>', views.studentpro, name='studentpro'),
    path('coursedetail/<id>', views.coursedetail, name='coursedetail'),
    path('courselist', views.enrollList, name='courselist'),
    path('teacherdash/<id>', views.teacherdash, name='teacherdash'),
    path('teacherpro/<id>', views.teacherpro, name='teacherpro'),
    path('coursedetailedit/<id>', views.coursedetailedit, name='coursedetailedit'),
    path('studentlist/<id>', views.studentlist, name='studentlist'),
    path('createcourse', views.createcourse, name='createcourse'),
    path('managequiz/<id>', views.managequiz, name='managequiz'),
    path('createquestion/<id>', views.createquestion, name='createquestion'),
    path('editquestion/<id>', views.editquestion, name='editquestion'),
    path('takequiz/<id>', views.takequiz, name='takequiz'),
    path('gradelist/', views.gradelist, name='gradelist'),
    path('quizzes/<id>', views.quizzes, name='quizzes'),
    path("listapi", views.ListAPI.as_view(), name="listapi"),
    path("createapi", views.CreateAPI.as_view(), name="createapi"),
    path("updateapi/<int:pk>", views.UpdateAPI.as_view(), name="updateapi"),
    path("deleteapi/<int:pk>", views.DeleteAPI.as_view(), name="deleteapi"),
]
