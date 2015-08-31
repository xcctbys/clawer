# coding=utf-8
''' gravatar imgs
'''

import md5
import urllib

from django.utils.safestring import mark_safe
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import exceptions

from html5helper.djuser import DjUser
from html5helper.decorator import static
from todo.models import UserProfile


register = template.Library()


@register.inclusion_tag("html5helper/tags/user_header.html")
def user_header(uid, size=16, mode="all"):
    """ mode's default is "all", you can select "name" or "img";
    """
    try:
        profile = UserProfile.objects.get(user_id=uid)
    except exceptions.ObjectDoesNotExist:
        return {"profile": None}
    
    img_url = profile.upload_header_url or _gravatar_url(profile.user, size)
    user_link = reverse(settings.USER_SHOW_VIEW, args=[uid])
    return {"img_url":img_url, "user_link":user_link, "profile":profile, "mode":mode, "size":size}
    

@register.inclusion_tag("html5helper/tags/ananymous_header.html")
def ananymous_header(uid, size=32):
    try:
        user = DjUser.get_by_pk(uid)
    except exceptions.ObjectDoesNotExist:
        return {"user":None}
    except ValueError:
        return {"user":None}

    return {"user":user, "size":size}


@register.filter("gravatar_img")
def do_gravatar_img(user, size=32):
    if not user:
        return ""
    
    img_url = user.get_profile().upload_header_url or _gravatar_url(user, size)
    return _generate_img(user, img_url, size)


@register.filter("gravatar_url")
def do_gravatar_url(user, size=32):
    if not user:
        return ""
    
    return _gravatar_url(user, size)


@register.filter("gravatar_user_url")
def do_gravatar_user_url(user):
    if not user:
        return ""
    
    return reverse(settings.USER_SHOW_VIEW, args=[user.id])


def _generate_img(user, url, sz):
    return mark_safe("<img src='%s' alt='%s' class='img-rounded' width='%d' height='%d' />" % (url, user.username, sz, sz))


def _gravatar_url(user, size=32, is_ananymous=False):
    """ use myself img
    """
    return static("img/tomato_user.png")

    query = urllib.urlencode({"s": size, "d": "identicon", "r":"g"})
    url_prefix = "http://www.gravatar.com/avatar"
    
    try:
        email = user.email
        if is_ananymous:
            email = md5.md5(user.email).hexdigest()[:6] + "@51zhi.com"
        path = "/%s?" % md5.md5(email.strip()).hexdigest() + query
    except:
        path = "/%s?" % md5.md5("webmaster@51zhi.com").hexdigest() + query
    
    url= url_prefix + path
    return url