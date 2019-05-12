from django.views.generic import (CreateView,UpdateView,ListView,DeleteView,DetailView)
from ..forms import TeacherSignUpForm,QuestionForm,BaseAnswerInlineFormSet
from ..models import User,Quizz,Question,Answer
from django.contrib.auth import login
from django.shortcuts import redirect
from django.db.models import Count,Avg
from django.contrib import messages
from django.urls import reverse_lazy,reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import inlineformset_factory
from django.db import transaction

class SignUpTeacher(CreateView):
    model=User
    form_class=TeacherSignUpForm
    template_name="classroom/signup.html"
    def form_valid(self,form):
        user=form.save()
        login(self.request,user)
        return redirect("home")
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['user_type']='teacher'
        return context
class TeacherQuizList(ListView):
    model=Quizz
    ordering=("name")
    context_object_name="quizzes"
    template_name="classroom/teacher/quizz_list.html"

    def get_queryset(self):
        teacher=self.request.user
        queryset=teacher.quizz.select_related('subject')\
            .annotate(question_count=Count("question",distinct=True))\
            .annotate(taken_count=Count("taken_quiz",distinct=True))
        return queryset

class CreateQuizz(CreateView):
    model=Quizz
    fields=('name','subject')
    template_name='classroom/teacher/create_quizz.html'
    def form_valid(self,form):
        quizz=form.save(commit=False)
        quizz.owner=self.request.user
        quizz.save()
        messages.success(self.request,"quizz created successfully")
        return redirect("teacher:quizz_list")

class UpdateQuizz(UpdateView):
    model=Quizz
    fields=('name','subject')
    template_name='classroom/teacher/update_quizz.html'
    
    def get_context_data(self,**kwargs):
        kwargs['questions']=self.get_object().question.annotate(answers_count=Count("answer"))
        return super().get_context_data(**kwargs)
    def get_queryset(self):
        queryset=self.request.user.quizz.all()
        return queryset
    def get_success_url(self):
        return reverse("teacher:quizz_update" ,kwargs={"pk":self.object.pk})

class DeleteQuizz(DeleteView):
    model=Quizz
    context_object_name='quizz'
    template_name="classroom/teacher/delete_quizz.html"
    success_url=reverse_lazy("teacher:quizz_list")

    def delete(self,request,*args,**kwargs):
        quizz=self.get_object()
        messages.success(request,"the %s deleted successfully" %quizz.name)
        return super().delete(self,request,*args,*kwargs)
    def get_queryset(self):
        return self.request.user.quizz.all()
class DetailQuizz(DetailView):
    model=Quizz
    context_object_name='quizz'
    template_name="classroom/teacher/detail_quizz.html"
    def get_queryset(self):
        return self.request.user.quizz.all()
    def get_context_data(self,**kwargs):
        quizz=self.get_object()
        taken_quizzes=quizz.taken_quiz.select_related('student__user',"question").order_by('-date')
        total_taken=taken_quizzes.count()
        quizz_avg_score=taken_quizzes.aggregate(avg_score=Avg('score'))
        
        extra_context={
            "taken_quizzes":taken_quizzes,
            "total_taken":total_taken,
            "total_taken":total_taken,
            "quizz_avg_score":quizz_avg_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)
def add_question(request,pk):
    quizz=get_object_or_404(Quizz,pk=pk,owner=request.user)
    
    if request.method=='POST':
        form=QuestionForm(request.POST)
        if form.is_valid:
            question=form.save(commit=False)
            question.quizz=quizz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect("teacher:answers_add", quizz.pk ,question.pk )
    else:
        form=QuestionForm()
        context={"quizz":quizz,"form":form}
        return render(request,"classroom/teacher/add_question.html",context)


def add_answers(request,quizz_pk,question_pk):
    quizz=get_object_or_404(Quizz,pk=quizz_pk,owner=request.user)
    question=get_object_or_404(Question,pk=question_pk,quizz=quizz_pk)
    AnswerInlineFormSet=inlineformset_factory(
                                    Question,
                                    Answer,
                                    min_num=2,
                                    max_num=5,
                                    validate_max=True,
                                    validate_min=True,
                                    formset=BaseAnswerInlineFormSet,
                                    fields=("text","is_correct"))
    if request.method=="POST":
        question_form=QuestionForm(request.POST,instance=question)
        answer_formset=AnswerInlineFormSet(request.POST,instance=question)
        #import pdb;pdb.set_trace()
        if question_form.is_valid() and answer_formset.is_valid():
            with transaction.atomic():
                question_form.save()
                answer_formset.save()
                messages.success(request, 'Question and answers saved with success!') 
            return redirect('teacher:quizz_list')
    else:
        question_form=QuestionForm(instance=question)
        answer_formset=AnswerInlineFormSet(instance=question)
    context={
                "question_form":question_form,
                "answer_formset":answer_formset,
                "quizz":quizz,
                "question":question

            }
    return render(request,"classroom/teacher/add_answers.html",context)

class QuestionDelete(DeleteView):
    model=Question
    context_object_name="question"
    template_name="classroom/teacher/delete_question.html"
    pk_url_kwarg='question_pk'

    def get_queryset(self):
        return Question.object.filter(quizz__owner=self.request.user)
    def get_context_data(self,**kwargs):
        question=self.get_object()
        kwargs["quiz"]=question.quiz
        return super().get_context_data(**kwargs)
    def delete(self,request,*args,**kwargs):
        question=self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(self,request,*args,**kwargs)
    def get_success_url(self):
        return reverse("teacher:update_quizz" ,kwargs={"pk":"quizz.pk"})
