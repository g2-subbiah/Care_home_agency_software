from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_staff_availability')
def get_staff_availability(staff_availability, date):
    return staff_availability.get(date, None)

@register.filter
def default_if_none_or_zero(value, default_text='-'):
    """
    Display default_text if value is None or 0.
    """
    if value is None or value == 0:
        return default_text
    return value