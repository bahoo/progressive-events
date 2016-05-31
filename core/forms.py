from django import forms
from django.utils.html import mark_safe
from .models import Event


# super hacky womp womp
class CheckboxSelectMultipleULAttrs(forms.CheckboxSelectMultiple):
    def __init__(self, ulattrs=None, attrs=None, choices=()):
            self.ulattrs = ulattrs
            super(CheckboxSelectMultipleULAttrs, self).__init__(attrs, choices)
            return

    def render(self, name, value, attrs=None, choices=()):
        html = super(CheckboxSelectMultipleULAttrs, self).render(name, value, attrs, choices)
        if not self.ulattrs:
            return html
        return mark_safe(html.replace('<ul', '<ul ' + self.ulattrs))


class SearchForm(forms.Form):
    distance = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'hidden', 'required': 'required'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden', 'required': 'required'}))
    days = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'hidden', 'required': 'required'}))
    event_types = forms.MultipleChoiceField(choices=Event.EVENT_TYPE_CHOICES, widget=CheckboxSelectMultipleULAttrs(ulattrs='class="list-unstyled hidden event-type-list"'))
