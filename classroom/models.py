from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student=models.BooleanField(default=False)
    is_teacher=models.BooleanField(default=False)

class Subject(models.Model):
    name=models.CharField(max_length=30)
    color=models.CharField(max_length=7,default="#007bff")
    def __str__(self):
        return self.name
class Quizz(models.Model):
    name=models.CharField(max_length=100)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="quizz")
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="quizz")
    def __str__(self):
        return self.name
class Question(models.Model):
    text=models.CharField("Question",max_length=255)
    quizz=models.ForeignKey(Quizz,on_delete=models.CASCADE,related_name='question')
    def __str__(self):
        return self.text
class Answer(models.Model):
    text=models.CharField("Answer",max_length=255)
    question=models.ForeignKey(Question,on_delete=models.CASCADE,related_name='answer')
    is_correct=models.BooleanField("Correct Answer",default=False)
    def __str__(self):
        return self.text
class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    quizz=models.ManyToManyField(Quizz,through="TakenQuiz")
    interests=models.ManyToManyField(Subject,related_name="student_intersted")
    answer=models.ManyToManyField(Answer)
    def __str__(self):
        return self.user.username
    def get_unanswered_questions(self,quizz):
        answered_question=self.answer.filter(answer__question__quizz=quizz)\
            .values_list("answer__question__pk",flat=True)
        unanswered_question=Question.objects.filter(quizz=quizz,student=self)\
                            .exclude(pk__in=answered_question)
class TakenQuiz(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="taken_quiz")
    quizz=models.ForeignKey(Quizz,on_delete=models.CASCADE,related_name="taken_quiz")
    score=models.IntegerField()
    date=models.DateTimeField(auto_now_add=True)

class StudentAnswer(models.Model):
     student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="student_answer")
     answer=models.ForeignKey(Answer,on_delete=models.CASCADE,related_name="student_answer")


