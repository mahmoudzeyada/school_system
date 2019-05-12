from django.shortcuts import render
from django.views.generic import TemplateView

def home(request):
    return render(request,"classroom/home.html")
class SignUPView(TemplateView):
    template_name="classroom/home_signup.html"
