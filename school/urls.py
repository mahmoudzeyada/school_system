
from django.contrib import admin
from django.urls import path,include
from classroom.views import home,student,teacher 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/',home.SignUPView.as_view(),name="signup"),
    path('accounts/signup/student/',student.SignUpStudent.as_view(),name="student_signup"),
    path('accounts/signup/teacher/',teacher.SignUpTeacher.as_view(),name="teacher_signup"),
    path('',include("classroom.urls"))
]
