from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import loader

from iran_list import settings


class ActionViewMixin(object):
    def post(self, request):
        # noinspection PyUnresolvedReferences
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # noinspection PyUnresolvedReferences
        return self._action(serializer)


class UserPasswordResetEmailFactory(object):
    token_generator = default_token_generator
    html_body_template_name = None

    subject_template_name = 'password_reset_email_subject.html'
    plain_body_template_name = 'password_reset_email_body.html'

    def __init__(self, from_email, user, protocol, domain, site_name, **context):
        self.from_email = from_email
        self.user = user
        self.domain = domain
        self.site_name = site_name
        self.protocol = protocol
        self.context_data = context

    @classmethod
    def from_request(cls, request, token, user=None, from_email=None, **context):
        site = get_current_site(request)
        from_email = from_email or getattr(
            settings, 'DEFAULT_FROM_EMAIL', ''
        )

        return cls(
            from_email=from_email,
            user=user or request.user,
            domain=settings.DOMAIN or site.domain,
            site_name=settings.SITE_NAME or site.name,
            protocol='https' if request.is_secure() else 'http',
            token=token,
            **context
        )

    def create(self):
        assert self.plain_body_template_name or self.html_body_template_name
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        if self.plain_body_template_name:
            plain_body = loader.render_to_string(
                self.plain_body_template_name, context
            )
            email_message = EmailMultiAlternatives(
                subject, plain_body, self.from_email, [self.user.email]
            )
            if self.html_body_template_name:
                html_body = loader.render_to_string(
                    self.html_body_template_name, context
                )
                email_message.attach_alternative(html_body, 'text/html')
        else:
            html_body = loader.render_to_string(
                self.html_body_template_name, context
            )
            email_message = EmailMessage(
                subject, html_body, self.from_email, [self.user.email]
            )
            email_message.content_subtype = 'html'
        return email_message

    def get_context(self):
        context = {
            'user': self.user,
            'domain': self.domain,
            'site_name': self.site_name,
            'protocol': self.protocol
        }
        context.update(self.context_data)
        return context
