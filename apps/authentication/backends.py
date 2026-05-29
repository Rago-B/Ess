import ssl
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend

class UnverifiedEmailBackend(DjangoEmailBackend):
    """
    Custom Email Backend that bypasses SSL verification for local development.
    Required for some GoDaddy SMTP configurations without valid local certs.
    """
    @property
    def ssl_context(self):
        context = super().ssl_context
        if context:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return context
