from django.shortcuts import render, redirect
from .models import Product, Category, Profile, Order, Customer
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import SignUpForm, UserInfoForm, UpdateUserForm, ChangePasswordForm
from django.http import JsonResponse, HttpResponse
from payment.forms import ShippingForm
from store.utils import send_mail_to_client
from django.template.loader import get_template
from django import forms
from django.db.models import Q, F
import json
from cart.cart import Cart
from .utils import send_mail_to_client
from payment.models import Order,OrderItem, ShippingAddress2
from django.contrib.auth.models import User


def orders(request, user_type):
        current_user = request.user.id

        if (user_type == 'user' or user_type == 'admin' ):
            shipment = ShippingAddress2.objects.get(user__id =current_user)
            orders = Order.objects.filter(user__id =current_user ).annotate(ship_date=F('date_shipped'), inv_date=F('invoice_date'))
            order_lines = OrderItem.objects.filter(user__id =current_user).annotate(linetotal=F('quantity') * F('price'))

        if (user_type == 'guest'):
            #shipment = ShippingAddress2.objects.get(user__id =None)
            orders = Order.objects.filter(user__id =None ).annotate(ship_date=F('date_shipped'), inv_date=F('invoice_date'))
            order_lines = OrderItem.objects.filter(user__id =None).annotate(linetotal=F('quantity') * F('price'))

            return render(request, "store_orders.html", {'user_type':user_type,'orders': orders, 'order_lines': order_lines})

        return render(request, "store_orders.html", {'user_type':user_type,'shipment':shipment,'orders':orders, 'order_lines':order_lines })

def invoice(request, full_name, shipping_address, email, phone, invoice_no, invoice_date, order_no, totals):
    current_user = request.user.id

    quantities = {}
    prod_totals = {}
    order_lines = OrderItem.objects.filter(order__id=order_no).annotate(linetotal=F('quantity') * F('price'))
    product_ids = []
    for lines in order_lines:
        product_ids.append(lines.product.pk)

    products = Product.objects.filter(id__in=product_ids)
    for line in order_lines:
        quantities[str(line.product.id)]=line.quantity
        prod_totals[str(line.product.id)]=line.linetotal
    html_content = get_template('payment/orderemail.html').render(
                {'full_name': full_name, 'shipping_address': shipping_address, 'email': email, 'phone': phone,
                'invoice_no': invoice_no, 'invoice_date': invoice_date,
                'order_no': order_no, 'cart_products': products, 'quantities': quantities, 'totals': totals,
                'prod_totals': prod_totals})
    #send_mail_to_client(None, full_name, email, phone, shipping_address, totals, html_content)
    return render(request, "payment/orderemail.html",
                  {'full_name': full_name, 'shipping_address': shipping_address, 'email': email, 'phone': phone,
                   'invoice_no': invoice_no, 'invoice_date': invoice_date,
                   'order_no': order_no, 'cart_products': products, 'quantities':quantities, 'totals': totals, 'prod_totals': prod_totals  })

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

def update_user_info(request, update_token):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        usr_form = UpdateUserForm(request.POST or None, instance=current_user)
        profile = Profile.objects.get(user__id=request.user.id)
        shipment = ShippingAddress2.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=profile)
        shipping_form = ShippingForm(request.POST or None, instance=shipment)

############   Implementing the Ajax call from user_information.html
############   For method = 'POST' it will be Ajax Call and saving the changes in the database.
############   After saving updated User/Profile/Shipping Info it will not reload the page.
############   After successful/unsuccessfull form validatin and saving into dabase
############   It will retuen a JsonRespose with appropiate message to show in the HTM alert div.
        if (request.method=='POST'):
            if update_token=='user':
                if usr_form.is_valid():
                    usr_form.save()
                    messages.success(request, "Your User Info Has Been Updated!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your User Info Has Not Been Updated!!"+json.dumps(usr_form.errors.as_data()))
                    return JsonResponse({'success': False, 'errors': form.errors})
            if update_token == 'profile':
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your Profile Info Has Been Updated!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your Profile Info Has Not Been Updated!!"+json.dumps(form.errors.as_data()))
                    return JsonResponse({'success': False, 'errors': form.errors})
            if update_token == 'shipping':
                if shipping_form.is_valid():
                    shipping_form.save()
                    messages.success(request, "Your Shipment Info Has Been Updated!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your Shipment Info Has Not Been Updated!!"+json.dumps(shipping_form.errors.as_data()))
                    return JsonResponse({'success': False, 'errors': form.errors})
            #if form.is_valid()  or shipping_form.is_valid():
            #    # Save original form
            #    form.save()
                # Save shipping form
            #    shipping_form.save()
            #current_user = User.objects.get(id=request.user.id)
            #profile = Profile.objects.get(user__id=request.user.id)
            #shipment = ShippingAddress2.objects.get(user__id=request.user.id)

            #return render(request, "user_information.html", {'user':current_user, 'profile':profile, 'shipment':shipment})
        else :
            return render(request, "user_information.html", {'profile':profile, 'shipment':shipment})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

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
    messages.success(request, ("Please input Correct UserName or Mobile No to Register."))
    if request.method == "POST":

    #    first_name = request.POST.get('first_name')
    #    last_name = request.POST.get('last_name')
    #    username   = request.POST.get('username')
    #    password1  = request.POST.get('password1')
    #    password2  = request.POST.get('password2')
    #    email = request.POST.get('email')
    #    form = SignUpForm(username=username, first_name=first_name, last_name=last_name, email=email, password1=password1, password2=password2)
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, form.save())
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
        else:
            messages.success(request, ("Woops! User Already Exists or Incorrect User Data to Register..."))
    else:
        form = SignUpForm()
    return render(request, "modalsignup.html", { "form": form })


def login_sidemenu(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
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
            messages.success(request, ("Woops! Incorrect User Name / Password."))
    else:
        form = AuthenticationForm()


    return render(request, "modalsignup.html", { "form": form })

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

import uuid
def forget_password(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')

            user = User.objects.filter(username=username).first()
            if user == None:
                messages.success(request, "User Not Found !!")
                return redirect('/forget_password')

            user_profile = Profile.objects.filter(user__id=user.id).first()

            #if user.first_name != None and user.last_name != None:
            #    full_name = "{} {}".format(user.first_name, user.last_name)
            #    full_name =  user.first_name+'  '+user.last_name
            #elif  user.last_name == None:
            full_name = user.first_name
            token = str(uuid.uuid4())
            subject = "Your Forget Password Link."
            reset_link = 'http://127.0.0.1:8000/update_password/'
            reset_email_link = 'http://127.0.0.1:8000/update_password_emaillink/'+str(user.id)+'/'+token+'/'

            user_profile.forget_password_token=token
            user_profile.save()

            html_content = get_template('forgetPass.html').render(
                {'user':user,'full_name': full_name, 'email': user.email, 'link':reset_email_link, 'user_id':str(user.id), 'token':token})

            send_mail_to_client(user=None,full_name=full_name, email=user.email, phone=user_profile.phone, shipping_address=None, amount_paid=None,html_content=html_content)

            return render(request, "forgetPass.html", {'user':user,'full_name': full_name, 'email': user.email, 'phone': user_profile.phone, 'link':reset_link, 'user_id':str(user.id), 'token':token})
            #return True
        else :
            return render(request, "forget_password.html")
    except Exception as e:
        print(e)
        return redirect("home")

def update_password_emaillink(request,userid,token):
    try :

        current_user = User.objects.get(pk=userid)
        db_token = Profile.objects.filter(user__id=userid).first().forget_password_token

        if db_token == token :
            if request.method == 'GET':
                form = ChangePasswordForm(current_user)
                return render(request, "update_password.html", {'form': form, 'token': token, 'userid': userid, 'user':current_user})
            else :
                return redirect('home')
        else:
                messages.success(request,'User Token is not matching with the User Profile Token.....')
                return redirect('home')
    except Exception as e:
        print(e)
        messages.error(request,e)
        return redirect('home')

def update_password(request):

###################    Reset of Password without Logged in User
###################    By Username, User are requested to click
###################    on the Reset Password Link forwarded to his/her's Email Id
    if request.method == 'POST':
        token = request.POST.get('token')
        user_id = request.POST.get('user_id')
        if user_id != None :
            db_token = Profile.objects.filter(user__id=user_id).first().forget_password_token
            user_id_reset = user_id
            current_user_reset = request.user
            request.session['user_id_reset'] = user_id_reset
            #request.session['current_user_reset'] = current_user_reset
            if token == db_token :
                request.session['token'] = token
                request.session['db_token'] = db_token


        #current_user_reset = request.session.get('current_user_reset')
        user_id_reset = request.session.get('user_id_reset')
        token = request.session.get('token')
        db_token = request.session.get('db_token')

        if user_id_reset != None or token == db_token:
            current_user = User.objects.get(pk=user_id_reset)
            form = ChangePasswordForm(current_user, request.POST)

            if form.is_valid():
                form.save()
                current_user.password = request.POST.get('new_password1')
                #current_user.save()
                messages.success(request, "Your Password Has Been Updated...Please Log-In with Your New Password. ")
                login(request, current_user)
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

            return render(request, "update_password.html", {'form': form})
################ End of Password Reset without User Login  ########################

##########  Password Reset Once user has been authenticated by his Login credential ##########
    if (request.user.is_authenticated):
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
