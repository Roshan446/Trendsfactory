from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from store.forms import RegistrationForm, LoginForm
from store.models import Product, BasketItem, Size, Order, OrderItems
from store import models
from store.decoraters import signin_required, owner_permission_required
# Create your views here.



decor = signin_required

    






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
@method_decorator([signin_required, never_cache], name="dispatch")
class ProductListView(View):
    def get(self, request, *args, **kwargs):
        qs = models.Product.objects.all()
        return render(request, "index.html", {"data": qs})


@method_decorator([signin_required, never_cache], name="dispatch")
class ProductDetailView(View):
    
    
    def get(self, request, *args, **kwargs):
        id =  kwargs.get("pk")
        qs = models.Product.objects.get(id =id)
        return render(request, "product_detail.html", {"data":qs})


class HomeView(TemplateView):
    template_name = "base.html"

@method_decorator([signin_required, never_cache], name="dispatch")
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


@method_decorator([signin_required, never_cache], name="dispatch")
class BasketItemsListView(View):


    def get(self, request, *args, **kwargs):
        qs = request.user.cart.cartitem.filter(is_ordered_placed = False)
        return render(request, "cart_list.html", {"data":qs})


@method_decorator([signin_required,owner_permission_required], name="dispatch")
class BasketItemRemoveView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        basket_item_obj = BasketItem.objects.get(id=id)
        basket_item_obj.delete()
        return redirect('basket-items')
    
@method_decorator([signin_required,owner_permission_required], name="dispatch")
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
    
@method_decorator([signin_required, never_cache], name="dispatch")
class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        
        return render(request, "checkout.html")
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        order_obj = Order.objects.create(user_object = request.user,
                             delivery_address = address,
                             email = email,
                             phone = phone,
                             total = request.user.cart.basket_total
                             
                             )
        # creating order item instance
        try:
            basket_items = request.user.cart.cart_item
            for bi in basket_items:
                OrderItems.objects.create(order_object = order_obj, 
                                      basket_item_object = bi)
                bi.is_ordered_placed = True
                bi.save()
        except:
            order_obj.delete()
        
        finally:
            return redirect("index")
    
class OrderSummary(View):
    def get(self, request, *args, **kwargs):
        qs = Order.objects.filter(user_object = request.user)
        return render(request, "order_summary.html", {"data":qs})
    
    
    
    # def get(self, request, *args, **kwargs):
    #     qs = request.user.purchase.purchaseitems

    #     return render(request, 'ordersummary.html', {"data":qs})

@method_decorator([signin_required, never_cache], name="dispatch")
class SignoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("signin")