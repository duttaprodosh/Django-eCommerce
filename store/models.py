from django.shortcuts import render, redirect
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

# There are four signals - pre_save, post_save, pre_delete, post_delete
# Automate the profile thing
post_save.connect(create_profile, sender=User)


# Categories of Products
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

#@daverobb2011
    class Meta:
        verbose_name_plural = 'categories'


# Customers
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)


    def __str__(self):
        return f'{self.first_name} {self.last_name}'



# All of our Products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
# Add Sale Stuff
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name


# Customer Orders
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product

class Department(models.Model):
    department_name = models.CharField(max_length=100)

    def __str__(self)->str:
        return self.department_name

    class Meta:
        ordering =['department_name']

class StudentID(models.Model):
    student_id = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.student_id

class StudentManger(models.Manager):
    def get_queryset(self):
       return super().get_queryset().filter(is_deleted=False)

class Student(models.Model):
    department = models.ForeignKey(Department, related_name="department", on_delete=models.CASCADE)
    student_id = models.OneToOneField(StudentID, related_name="studentid", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age   = models.IntegerField(default=18)
    address = models.TextField()
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()  # The default manager.
    admin_objects = StudentManger()  # The StudentManger -specific manager.

    def __str__(self) ->str:
        return self.name
    class Meta:
        ordering = ['name']
        verbose_name = "student"

################   django Signals ###################################
class Car(models.Model):
    car_name = models.CharField(max_length=200)
    speed    = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.car_name}"

#  As soon as Car Object created it will call car_speed_api
@receiver(post_save, sender=Car)
def car_spped_api(sender, instance, **kwargs):
    print("CAR OBJECT CREATED")
    print(sender, instance, kwargs)
################   django Signals ###################################

def category(request, foo):
# Replace Hyphens with Spaces
    foo = foo.replace('-', ' ')
# Grab the category from the url
    try:
# Look Up The Category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("That Category Doesn't Exist..."))
        return redirect('home')





