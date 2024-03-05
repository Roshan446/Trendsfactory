from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from store.forms import RegistrationForm, LoginForm
from django.contrib.auth import login, logout, authenticate
from store.models import Product, BasketItem, Size
from store import models
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
# Create your views here.

def signin_required(fn):
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return redirect('signin')


decor = signin_required

method_decorator(signin_required, name='dispatch')
    






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


class AddToBasketView(View):
    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        product_object = Product.objects.get(id =id)
        size =request.POST.get("size")
        size_obj = Size.objects.get(name = size)
        qty =request.POST.get("qty")

        BasketItem.objects.create(
            product_object = product_object,
            size_object = size_obj,
            qty =qty,
            basket_object = request.user.cart

        )
        return redirect("index")

class BasketItemsListView(View):


    def get(self, request, *args, **kwargs):
        qs = request.user.cart.cartitem.filter(is_ordered_placed = False)
        return render(request, "cart_list.html", {"data":qs})



class BasketItemRemoveView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        basket_item_obj = BasketItem.objects.get(id=id)
        basket_item_obj.delete()
        return redirect('basket-items')

class CartItemUpdateQtyView(View):


    def post(self, request, *args, **kwargs):
        action = request.POST.get("counterbutton")
        id = kwargs.get("pk")
        basket_item_object = BasketItem.objects.get(id=id)
        if action =="+":
            basket_item_object.qty +=1
            basket_item_object.save()
        else:
            basket_item_object.qty -=1
            basket_item_object.save() 
        return redirect("basket-items")

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        
        return render(request, "checkout.html")
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        print(email, phone, address)
        return redirect("index")

