from django.shortcuts import render, redirect
from .models import Product, Category, Profile, Order, Customer
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import SignUpForm, UserInfoForm, UpdateUserForm, ChangePasswordForm

from payment.forms import ShippingForm


from django import forms
from django.db.models import Q, F
import json
from cart.cart import Cart
from .utils import send_mail_to_client
from payment.models import Order,OrderItem, ShippingAddress2
from django.contrib.auth.models import User


def orders(request):
    current_user = request.user.id

    shipment = ShippingAddress2.objects.get(user__id =current_user)
    orders = Order.objects.filter(user__id =current_user ).annotate(ship_date=F('date_shipped'))
    order_lines = OrderItem.objects.filter(user__id =current_user).annotate(linetotal=F('quantity') * F('price'))

    return render(request, "orders.html", {'shipment':shipment,'orders':orders, 'order_lines':order_lines })

def search(request):

	# Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        # Query The Products DB Model
        category = Category.objects.filter(Q(name__icontains=searched))
        products = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched) | Q(category__in=category))
        # Test for null
        if not products:
            messages.success(request, "That Product Does Not Exist...Please try Again.")
            return render(request, "search.html", {})
        else:
            return render(request, "home.html", {'products':products,'searchvalue':request.POST['searched']})
    else:
        return render(request, "search.html", {})

def update_info(request):
    if request.user.is_authenticated:
        # Get Current User
        current_user = Profile.objects.get(user__id=request.user.id)
        # Get Current User's Shipping Info
        shipping_user = ShippingAddress2.objects.get(user__id=request.user.id)

        # Get original User Form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Get User's Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid()  or shipping_form.is_valid():
            # Save original form
            form.save()
            # Save shipping form
            shipping_form.save()

            messages.success(request, "Your Info Has Been Updated!!")
            return redirect('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form':shipping_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
	return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)

            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop thru the cart and add the items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You Have Been Logged In!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, please try again..."))
            return redirect('login')
    else :
        #form = AuthenticationForm()
        return render(request, 'login.html', {})

def modalsignup(request):
        return render(request, 'modalsignup.html')

def register_sidemenu(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
    else:
        form = UserCreationForm()
    return render(request, "register_sidemenu.html", { "form": form })


def login_sidemenu(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print(form.get_user())
            login(request, form.get_user())
            if form.get_user() is not None:
                # Do some shopping cart stuff
                current_user = Profile.objects.get(user__id=request.user.id)

                # Get their saved cart from database
                saved_cart = current_user.old_cart
                # Convert database string to python dictionary
                if saved_cart:
                    # Convert to dictionary using JSON
                    converted_cart = json.loads(saved_cart)
                    # Add the loaded cart dictionary to our session
                    # Get the cart
                    cart = Cart(request)
                    # Loop thru the cart and add the items from the database
                    for key, value in converted_cart.items():
                        cart.db_add(product=key, quantity=value)

                messages.success(request, ("You Have Been Logged In!"))

            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login_sidemenu.html", { "form": form })

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out...Thanks for stopping by..."))
    return redirect('home')

def register_user(request):
    messages.success(request, ("Please input UserName or Mobile No to Register."))
    form = SignUpForm()
    if request.method == "POST":
        #form = UserCreationForm(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
        else:
            messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
            return redirect('register')
            #form = UserCreationForm()

    else:
        # form = UserCreationForm()
        return render(request, 'register.html', {'form': form})


def product(request,pk):
	product = Product.objects.get(id=pk)
	return render(request, 'product.html', {'product':product})

def category(request, foo):
    # Replace Hyphens with Spaces


    foo = foo.replace('-', ' ')
    # Grab the category from the url
    try:
    # Look Up The Category
        if foo == 'Deals':
            products = Product.objects.filter(is_sale = True)
            category= 'Deals of the Day'
            foo = 'Deals of the Day'
            print(products[0].name)
        else :
            category = Category.objects.filter(Q(name__icontains=foo))
            products = Product.objects.filter(Q(name__icontains=foo) | Q(description__icontains=foo) | Q(category__in=category))

        #category = Category.objects.get(name=foo)
        #products = Product.objects.filter(category=category)
        if foo == 'phone':
            foo = 'Mobile Phones'
        if foo == 'book':
            foo = 'All Books'
        if foo == 'phone':
            foo = 'All Mobile Phones'
        if foo == 'programming books':
            foo = 'Programming Books'
        if foo == 'marketing books':
            foo = 'Marketing Books'

        return render(request, 'category.html', {'products':products, 'category':category, 'input_category':foo})
    except:
        messages.success(request, ("That Category Doesn't Exist..."))
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated!!")
            return redirect('home')
        return render(request, "update_user.html", {'user_form':user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method  == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

def send_mail_to_customer(request):
    send_mail_to_client()
    return redirect('home')
