from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import  post_save

class Category(models.Model):
    name=models.CharField(max_length=200,unique=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    name=models.CharField(max_length=150,unique=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length = 200, unique =True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField(null=True)
    image=models.ImageField(upload_to="product_images",default="default.jpg",null=True,blank=True)
    category_object=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="item")
    size_object=models.ManyToManyField(Size)
    price=models.PositiveIntegerField()
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    tag_objects = models.ManyToManyField(Tag, null = True)

    def __str__(self):
        return self.title

class Basket(models.Model):
    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    @property
    def cart_item(self):
        return self.cartitem.filter(is_ordered_placed =False)
    
    @property
    def item_count(self):
        return self.cart_item.count()
    @property
    def basket_total(self):
        basket_item = self.cart_item
        if basket_item:
            total = sum([bi.item_total for bi in basket_item])
            return total
        else:
            return 0
    





class BasketItem(models.Model):
    product_object=models.ForeignKey(Product,on_delete=models.CASCADE)
    qty=models.PositiveIntegerField(default=1)
    basket_object=models.ForeignKey(Basket,on_delete=models.CASCADE,related_name="cartitem")
    size_object = models.ForeignKey(Size, on_delete = models.CASCADE, null= True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    is_ordered_placed = models.BooleanField(default = False)
    @property
    def item_total(self):
        return self.qty * self.product_object.price

class Order(models.Model):

    user_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="purchase")
    delivery_address=models.CharField(max_length=200)
    phone=models.CharField(max_length=12)
    is_paid=models.BooleanField(default=False)
    total=models.PositiveIntegerField()
    email = models.CharField(max_length = 200, null = True)
    order_id=models.CharField(max_length=200,null=True)

    options=(
        ("cod","cod"),
        ("online","online")
    )
    payment=models.CharField(max_length=200,choices=options,default="cod")
    option=(
        ("order-placed","order-placed"),
        ("intransit","intransit"),
        ("dispatched","dispatched"),
        ("delivered","delivered"),
        ("cancelled","cancelled")
    )
    status=models.CharField(max_length=200,choices=option,default="order-placed")
    
    @property
    def get_order_items(self):
        return self.purchaseitems.all()

    
    @property
    def get_order_total(self):
        purchase_items=self.get_order_items
        order_total=0
        if purchase_items:
            order_total=sum([pi.basket_item_object.item_total for pi in purchase_items])
        return order_total


class OrderItems(models.Model):
    order_object=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="purchaseitems")
    basket_item_object=models.ForeignKey(BasketItem,on_delete=models.CASCADE)





def create_basket(sender, instance, created, **kwargs):
    if created:
        Basket.objects.create(owner = instance)

post_save.connect(create_basket, sender= User)


