from django import template

from la_facebook.models import UserAssociation

register = template.Library()


@register.filter
def authed_via(user):
    if user.is_authenticated():
        try:
            assoc = UserAssociation.objects.get(user=user)
        except UserAssociation.DoesNotExist:
            return False
        return assoc.expired()
    else:
        return False
    
@register.simple_tag
def profile_pic_src(user, type='normal'):
    """
    Returns url for user's Facebook profile. The url format is:
    
        http://graph.facebook.com/<fb id>/picture?type=<type>
        
    Valid type values are: small, normal, large.
    """
    if user.is_authenticated():
        try:
            assoc = UserAssociation.objects.get(user=user)
        except UserAssociation.DoesNotExist:
            return ''
        url = 'http://graph.facebook.com/%s/picture?type=%s'
        return url % (assoc.identifier, type)
    else:
        return ''
    
@register.simple_tag
def get_friends_list(user):
    """
    Returns url for user's Facebook profile. The url format is:
    
        http://graph.facebook.com/<fb id>/picture?type=<type>
        
    Valid type values are: small, normal, large.
    """
    if user.is_authenticated():
        try:
            assoc = UserAssociation.objects.get(user=user)
        except UserAssociation.DoesNotExist:
            return ''
        url = 'http://graph.facebook.com/me/friends?type=%s'
        return url % (assoc.identifier, type)
    else:
        return ''
 
