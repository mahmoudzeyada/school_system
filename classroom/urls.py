from django.urls import path,include
from .views import home,student,teacher


urlpatterns = [
    path("",home.home,name="home"),
    #student
    path("students/",include(([
        path("pref/",student.StudentIntersted.as_view(),name="update_interstes"),
        path("quizzes/",student.StudentQuizList.as_view(),name="quizzes_list"),
        path("taken_quizzes/",student.StudentTakenQuizList.as_view(),name="quizzes_taken_list"),
        path("quiz/<int:pk>/",student.taken_quiz,name="take_quiz"),

        ]
        
        ,"classroom"),namespace="student")),
    
    #teacher

        path("teachers/",include(([
        path("quizz_list/",teacher.TeacherQuizList.as_view(),name="quizz_list"),
        path("quizz_create/",teacher.CreateQuizz.as_view(),name="quizz_create"),
        path("quizz_update/<int:pk>/",teacher.UpdateQuizz.as_view(),name="quizz_update"),
        path("quizz_delete/<int:pk>/",teacher.DeleteQuizz.as_view(),name="quizz_delete"),
        path("quizz_details/<int:pk>/",teacher.DetailQuizz.as_view(),name="quizz_details"),
        path("question_add/<int:pk>/",teacher.add_question,name="question_add"),
        path("answers_add/quiz/<int:quizz_pk>/question/<int:question_pk>",teacher.add_answers,name="answers_add"),
        path("question_delete/<int:question_pk>/",teacher.add_question,name="question_delete"),

        

        ]
        
        ,"classroom"),namespace="teacher"))
]