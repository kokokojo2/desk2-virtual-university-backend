from Desk2.celery import app
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .tokens import TwoFATokenGenerator
from .models import UserAccount


@app.task
def send_2fa_token(user_id):
    """
    Sends token for 2FA authentication asynchronously using celery queue.
    """
    user = UserAccount.objects.get(pk=user_id)
    print('hello guy')
    token_generator = TwoFATokenGenerator()
    email_body = render_to_string(f'email/twoFA-auth.html', {
        'user': user,
        'token': token_generator.make_token(user),
    })

    return send_mail('Desk2 Team', email_body, 'noreply@desk2.com', [user.email], fail_silently=False)


