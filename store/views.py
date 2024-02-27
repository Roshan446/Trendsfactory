from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from store.forms import RegistrationForm, LoginForm
from django.contrib.auth import login, logout, authenticate
from store import models
from django.contrib import messages
# Create your views here.



class SignupView(View):
    def get(self, request, *args, **Kwargs):
        form =  RegistrationForm()
        return render(request, "login.html", {"form":form})
    
    def post(self, request, *args, **Kwargs):
        form =  RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signin")
        else:
            return render(request, "login.html", {"form":form})

class SigninView(View):
    def get(self, request, *args, **Kwargs):
        form = LoginForm()
        return render(request, "login.html", {"form":form})
    def post(self, request, *args, **Kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            u_name = form.cleaned_data.get("username")
            pwd = form.cleaned_data.get("password")
            user_auth = authenticate(request, username = u_name, password = pwd)
            if user_auth:
                login(request, user_auth)
                return redirect("index")
        messages.error(request, "invalid credential")
        return render(request, "login.html", {"form":form})
            
# class IndexView(View):
#     def get(self, request, *args, **Kwargs):
#         return render(request, "index.html")

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        qs = models.Product.objects.all()
        return render(request, "index.html", {"data": qs})

class ProductDetailView(View):
    
    
    def get(self, request, *args, **kwargs):
        id =  kwargs.get("pk")
        qs = models.Product.objects.get(id =id)
        return render(request, "product_detail.html", {"data":qs})


class HomeView(TemplateView):
    template_name = "base.html"
    
    