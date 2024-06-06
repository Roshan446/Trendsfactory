from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from store.forms import RegistrationForm, LoginForm
from store.models import Product, BasketItem, Size, Order, OrderItems, Tag
from store import models
from store.decoraters import signin_required, owner_permission_required

import razorpay

# Create your views here.



decor = signin_required

Key_id = "rzp_test_SnJESp7rS0B4eX"
key_secret  = "ZuAe8gC2opcR9yStlmyo2nN9"






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
        cat_qs = models.Category.objects.all()
        tags = models.Tag.objects.all()
        selected_cat = request.GET.get("category")
        if selected_cat:
            qs =qs.filter(category_object__name=selected_cat)

        return render(request, "index.html", {"data": qs, "data1":cat_qs, "tags":tags})
    def post(self, request, *args, **kwargs):
        tag_name = request.POST.get("tag")
        tags = models.Tag.objects.all()

        qs = Product.objects.filter(tag_objects__name = tag_name)
        return render(request, "index.html", {"data":qs, "tags":tags })

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
        payment_method =request.POST.get("payment")
        order_obj = Order.objects.create(user_object = request.user,
                             delivery_address = address,
                             email = email,
                             phone = phone,
                             total = request.user.cart.basket_total,
                             payment = payment_method
                             
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
            if payment_method == "online" and order_obj:
                client = razorpay.Client(auth=(Key_id, key_secret))
                data = { "amount": order_obj.get_order_total *100, "currency": "INR", "receipt": "order_rcptid_11" }
                payment = client.order.create(data=data)
                order_obj.order_id = payment.get("id")
                order_obj.save()

                context = {
                    "key":Key_id,
                    "order_id": payment.get("id"),
                    "amount": payment.get("amount") 
                }
                return render(request, "payment.html", {"context":context})

            
            return redirect("index")
    
# class OrderSummary(View):
#     def get(self, request, *args, **kwargs):
#         qs = Order.objects.filter(user_object = request.user)
#         return render(request, "order_summary.html", {"data":qs})
    
    
    
    # def get(self, request, *args, **kwargs):
    #     qs = request.user.purchase.purchaseitems

    #     return render(request, 'ordersummary.html', {"data":qs})

@method_decorator([signin_required, never_cache], name="dispatch")
class SignoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("signin")

class OrderSummaryView(View):
    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user_object=request.user).exclude(status = "cancelled")
        return render (request,"order_summary.html",{"data":qs})
    
class OrderItemRemoveView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        OrderItems.objects.get(id=id).delete()
        return redirect("summary")
    
@method_decorator(csrf_exempt, name="dispatch")
class PaymentVerificationView(View):
    def post(self, request, *args, **kwrags):
        client = razorpay.Client(auth=(Key_id, key_secret))
        data = request.POST
        try:
            client.utility.verify_payment_signature(data)
            print("********TRANSACTION COMPLETED***********")
            print(data)
            order_obj = Order.objects.get(order_id = data.get("razorpay_order_id"))
            order_obj.is_paid = True
            order_obj.save()

        except:
            print("!!!!!!!!!!!!transaction failed!!!!!!!!!!!")

        return render(request, 'success.html')

