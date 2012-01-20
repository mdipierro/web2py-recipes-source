# coding: utf8

MAX_LOGIN_FAILURES = 3
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

def _():
    from gluon.tools import Recaptcha
    key = 'login_from:%s' % request.env.remote_addr
    num_login_attempts = cache.ram(key,lambda:0,None)
    if num_login_attempts >= MAX_LOGIN_FAILURES:
        auth.settings.login_captcha = Recaptcha(
           request,RECAPTCHA_PUBLIC_KEY,RECAPTCHA_PRIVATE_KEY)
    def login_attempt(form,key=key,n=num_login_attempts+1):
        cache.ram(key,lambda n=n:n,0)
    def login_success(form,key=key):
        cache.ram(key,lambda:0,0)
    auth.settings.login_onvalidation.append(login_attempt)
    auth.settings.login_onaccept.append(login_success)
_()
