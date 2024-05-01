from django.shortcuts import render, redirect
from cart.cart import Cart
#from payment.forms import ShippingForm, PaymentForm
#from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product

def payment_success(request):
	return render(request, "payment/payment_success.html", {})

