# Some custom filters for dictionary lookup.
from django.template.defaultfilters import register

@register.filter(name='dictlookup')
def dictlookup(dict, index):
    print index
    if index in dict:
        return dict[index]
    return ''
