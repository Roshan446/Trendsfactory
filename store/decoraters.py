from django.shortcuts import redirect
from store.models import BasketItem, Basket
from django.contrib import messages
def signin_required(fn):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "invalid user")
            return redirect("signin")
        else:
            return fn(request,*args, **kwargs)
        
    return wrapper


def owner_permission_required(fn):
    def wrapper(request,*args,**kwargs):
        id =kwargs.get(id =id)
        basket_item = BasketItem.objects.get(id=id)
        if basket_item.basket_object.owner != request.user:
            messages.error(request, "access denied")
            return redirect("signin")
        else:
            return fn(request, *args, **kwargs)
        return wrapper

