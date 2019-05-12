from django.contrib import messages
from django.views.generic import (CreateView,UpdateView,ListView)
from ..forms import (StudentSignUpForm,StudentInterstesForm,StudentTakeQuiz)
from ..models import (User,Student,Quizz,TakenQuiz)
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy,reverse
from django.db.models import Count
from django.db import transaction

class SignUpStudent(CreateView):
    model=User
    form_class=StudentSignUpForm
    template_name="classroom/signup.html"
    def form_valid(self,form):
        user=form.save()
        login(self.request,user)
        return redirect("home")
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['user_type']='student'
        return context

class StudentIntersted(UpdateView):
    model=Student
    template_name = 'classroom/students/interests_form.html'
    form_class=StudentInterstesForm
    success_url=reverse_lazy("home")
    def form_valid(self,form):
        messages.success(self.request,'Interests updated with success!')
        return super().form_valid(form)
    def get_object(self):
        return self.request.user.student

class StudentQuizList(ListView):
    model=Quizz
    context_object_name="quizzes"
    template_name = 'classroom/students/quiz_list.html'
    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizz.values_list('pk', flat=True)
        queryset = Quizz.objects.filter(subject__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('question')) \
            .filter(questions_count__gt=0)
        return queryset
    
class StudentTakenQuizList(ListView):
    model=TakenQuiz
    ordering=('date')
    context_object_name="taken_quizzes"
    template_name='classroom/students/quiz_taken_list.html'
    def get_queryset(self):
        queryset=self.request.user.student.taken_quiz.\
            select_related('quizz','quizz__subject').order_by('quizz__name')
        return queryset

def taken_quiz(request,pk):
    quizz=get_object_or_404(Quizz,pk=pk)
    student=request.user.student
    if student.quizz.filter(pk=pk).exists():
        return reverse("quizzes_taken_list")
    
    total_questions = quizz.question.count()
    unanswered_questions = student.get_unanswered_questions(quizz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()
    
    if request.method=="POST":
        form=StudentTakeQuiz(question=question,data=request.POST)
        if form.is_valid():
            with transaction.atomic:
                student_answer=form.save(commit=False)
                student_answer.student=student
                student_answer.save()
            if student.get_unanswered_questions(quizz).exists():
                return redirect('student:take_quiz',pk)
            else:
                correct_answer=student.answer.filter(question__quizz=quizz,is_correct=True).count()
                score = round((correct_answers / total_questions) * 100.0, 2)
                TakenQuiz.objects.create(quizz=quizz,student=student,score=score)
                if score < 50.0:
                    messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                else:
                    messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                return redirect('student:quizzes_list')
    else:
        form=StudentTakeQuiz()
        return render(request, 'classroom/students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
                                })



    
