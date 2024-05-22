from .models import Student
import time
from django.core.mail import send_mail
from django.conf import settings

def send_mail_to_client(user, full_name, email, shipping_address, amount_paid):
    subject = 'Mail from Python djangoECommerce application.'
    message = "Hi "+full_name+", "+"""
    \n\tHow Are you ? Thanks for shopping in the Django EComm site.
    """+"\n\n\t Your Order has been Shipped to the address : "+"\n"+shipping_address+"\n\n\t Amount Paid : "+"Rs. "+str(amount_paid)+"""
    \n\n\tDjango ECommerce App sending this email. \n\n Thanks,\ndjangoEComm App Admin.    
    """
    from_email = settings.EMAIL_HOST_USER
    sender_email_id_password=settings.EMAIL_HOST_PASSWORD
    recipient_list = ['duttaprodosh@gmail.com']
    file_path = f"{settings.BASE_DIR}/main.xlsx"

    #import smtplib
    #from email.message import EmailMessage
    #import ssl

    from django.core.mail import EmailMessage

    em = EmailMessage(subject=subject, body=message, from_email=from_email, to = recipient_list, cc=None, bcc=None, reply_to=None)

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
    em.send()


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
