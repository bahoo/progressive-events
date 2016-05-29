from django import template

register = template.Library()

@register.simple_tag
def event_dates(event, **kwargs):
    return event.dates(**dict((k,int(v)) for k, v in kwargs.iteritems()))