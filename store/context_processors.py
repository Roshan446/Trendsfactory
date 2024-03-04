def dummy(request):
    return {"msg":"hello world"}

def basket_count(request):
    if request.user.is_authenticated:
        count = request.user.cart.item_count
        return{"cart_count":count}
    else:
        return{"cart_count":0}