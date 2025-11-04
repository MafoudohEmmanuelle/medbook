from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def send_account_email(user, temp_password=None, confirm_url=None, role_label="User"):
    """
    Sends an account creation email for any role.
    - confirm_url: include confirmation link (for patients)
    - temp_password: include login credentials (for doctors/managers)
    - role_label: string describing the role in the email
    """
    subject = _(f"Welcome to MedBook - {role_label} Account Created")
    message = f"Hello {user.first_name},\n\n"

    if confirm_url:
        message += _(f"Please confirm your email by clicking the link below:\n{confirm_url}\n\n")
    elif temp_password:
        message += _(f"You have been registered as a {role_label.lower()} on the MedBook platform.\n\n"
                     f"Your login credentials are:\nEmail: {user.email}\nTemporary Password: {temp_password}\n\n"
                     "Please log in and change your password after first login.\n\n")
    else:
        message += _("Your account has been successfully created on MedBook.\n\n")

    message += _("Best regards,\nThe MedBook Team")

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )
