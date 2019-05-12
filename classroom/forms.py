
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from .models import (User,Student,Subject,Answer,Question)

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model=User
    def save(self,commit=True):
        user=super().save(commit=False)
        user.is_teacher=True
        user.save()
        return user
class StudentSignUpForm(UserCreationForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True)
    class Meta(UserCreationForm.Meta):
        model=User
    @transaction.atomic
    def save(self,commit=True):
        user=super().save(commit=False)
        user.is_student=True
        user.save()
        student=Student.objects.create(user=user)
        student.interests.add(*self.cleaned_data.get("interests"))
        return user
class StudentInterstesForm(forms.ModelForm):
    class Meta :
        model=Student
        fields=('interests',)
        widgets={"interests":forms.CheckboxSelectMultiple}
    
class StudentTakeQuiz(forms.ModelForm):
    class Meta:
        model=Student.answer.through
        fields=['answer']
    answer=forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=True

    )
    def __init__(self,*args,**kwargs):
        question=kwargs['question'].pop()
        super().__init__(*args,**kwargs)
        self.fields['answer'].queryset=question.answer.order_by('text')


class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields=("text",)

class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_at_least_one_correct=False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE',False):
                if form.cleaned_data.get('is_correct',False):
                    has_at_least_one_correct=True
        if not has_at_least_one_correct:
            raise ValidationError('set at least one correct',code="no_correct_answer_error")
