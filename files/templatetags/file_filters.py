from django import template

register = template.Library()

@register.filter
def ext_in(filename, extensions):
    """Check if file extension is in given list"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    ext_list = [e.strip() for e in extensions.split(',')]
    return ext in ext_list
