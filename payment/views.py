from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product

def payment_success(request):
	return render(request, "payment/payment_success.html", {})


def checkout(request):
	# Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	# Begin - Calculating Cart Product and quantity wise totol price
	prod_totals = {}
	prod_val = cart.get_prods_dict()
	prod_qty = cart.get_quants_dict()

	for i in range(len(prod_val)):
		for key, value in prod_qty.items():
			# Convert key string into into so we can do math
			key = int(key)
			if key == prod_val[i]['id']:
				if prod_val[i]['is_sale']:
					price = prod_val[i]['sale_price']
				else:
					price = prod_val[i]['price']
				prod_totals[str(key)] = float(value * price)

	# End - Calculating Cart Product and quantity wise totol price

	if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, "payment/checkout.html",
					  {"cart_products": cart_products, "quantities": quantities, "totals": totals,
					   "shipping_form": shipping_form, "prod_totals":prod_totals})
	else:
		# Checkout as guest
		shipping_form = ShippingForm(request.POST or None)
		return render(request, "payment/checkout.html",
					  {"cart_products": cart_products, "quantities": quantities, "totals": totals,
					   "shipping_form": shipping_form, "prod_totals":prod_totals})


def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Create a session with Shipping Info
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Check to see if user is logged in
		if request.user.is_authenticated:
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html",
						  {"cart_products": cart_products, "quantities": quantities, "totals": totals,
						   "shipping_info": request.POST, "billing_form": billing_form})

		else:
			# Not logged in
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html",
						  {"cart_products": cart_products, "quantities": quantities, "totals": totals,
						   "shipping_info": request.POST, "billing_form": billing_form})

		shipping_form = request.POST
		return render(request, "payment/billing_info.html",
					  {"cart_products": cart_products, "quantities": quantities, "totals": totals,
					   "shipping_form": shipping_form})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')
