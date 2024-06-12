from .models import Student
import time
from django.core.mail import send_mail
from django.conf import settings
import socket

def send_mail_to_client(user, full_name, email, phone, shipping_address, amount_paid,html_content):
    socket.getaddrinfo('127.0.0.1', 8000)
    if shipping_address== None :
        shipping_address=' '
    if amount_paid == None :
        amount_paid = 0
    subject = 'Mail from Python djangoECommerce application.'
    message = "Hi "+full_name+", "+"""
    \n\tHow Are you ? Thanks for shopping in the Django EComm site.
    """+"\n\n\t Your Order has been Shipped to the address : "+"\n"+shipping_address+"\n\n\t Amount Paid : "+"Rs. "+str(amount_paid)+"""
    \n\n\tDjango ECommerce App sending this email. \n\n Thanks,\ndjangoEComm App Admin.    
    """
    from_email = settings.EMAIL_HOST_USER
    sender_email_id_password=settings.EMAIL_HOST_PASSWORD
    #recipient_list = ['duttaprodosh@gmail.com']
    recipient_list = list(email.split(" "))
    file_path = f"{settings.BASE_DIR}/main.xlsx"

    #import smtplib
    #from email.message import EmailMessage
    #import ssl

    from django.core.mail import EmailMessage

#    em = EmailMessage(subject=subject, body=message, from_email=from_email, to = recipient_list, cc=None, bcc=None, reply_to=None)
    em = EmailMessage(subject=subject, body=html_content, from_email=from_email, to = recipient_list, cc=None, bcc=None, reply_to=None)
    em.content_subtype="html"
#######   Earlier Method of Sending mail using Python Library not Django mail package  #########
#    em['From'] = from_email
#    em['To']   = recipient_list
#    em['Subject'] = subject
#    em.set_content(message)
#    context = ssl.create_default_context()

#    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#        smtp.login(from_email, sender_email_id_password)
#        smtp.sendmail(from_email, recipient_list, em.as_string())
#        smtp.quit()
################################################################################################

######   Sending email using django library package    #########################################
#    em.attach_file(file_path)    ###  if you want to attach a file "main.xlsx"
    try :
        em.send()
    except Exception as e:
        print("Exception Raised (Not able to send Html content in the email. :"+str(e))
        em.content_subtype = "text"
        try :
            em.send()
        except Exception as e:
            print("Exception Raised (Not able to send Text email. :" + str(e))

    # creates SMTP session
    #s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    #s.starttls()
    # Authentication
    #s.login('duttaprodosh@gmail.com', '')
    # message to be sent
    # sending the mail
    #s.sendmail(from_email, recipient_list, message)
    # terminating the session
    #s.quit()
