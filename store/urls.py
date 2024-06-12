from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('login_sidemenu/', views.login_sidemenu, name="login_sidemenu"),
    path('modalsignup/', views.modalsignup, name="modalsignup"),
    path('forget_password/', views.forget_password, name="forget_password"),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('register_sidemenu/', views.register_sidemenu, name='register_sidemenu'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_password_emaillink/<str:userid>/<str:token>/', views.update_password_emaillink, name='update_password_emaillink'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('update_user_info/<str:update_token>', views.update_user_info, name='update_user_info'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('search/', views.search, name='search'),
    path('send_mail_to_customer/', views.send_mail_to_customer, name='send_mail_to_customer'),
    path('orders/<str:user_type>', views.orders, name='orders'),
    path('invoice/<str:full_name>/<str:shipping_address>/<str:email>/<str:phone>/<str:invoice_no>/<str:invoice_date>/<str:order_no>/<str:totals>', views.invoice, name='invoice'),
    #path('invoice/<str:invoice_no>', views.invoice, name='invoice'),
]