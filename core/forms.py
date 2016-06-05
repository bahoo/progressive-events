from django.contrib.gis import forms
from django.contrib.gis.forms import PointField
from django.utils.html import mark_safe
from .models import Event, Venue, Organization


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


class VenueForm(forms.ModelForm):
    venue_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Venue
        exclude = ['slug']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
        labels = {
            'title': 'Venue Name',
            'url': 'URL'
        }

    class Media:
        js = ('js/sigo.js', 'js/add-form.js')




class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        exclude = []
        labels = {
            'url': 'URL'
        }


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = ['venue', 'host']
        labels = {
            'start': 'Start Time',
            'end': 'End Time',
            'recurrences': 'Date / Recurring Schedule',
            'url': 'URL'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start': forms.TimeInput(attrs={'type': 'time'}),
            'end': forms.TimeInput(attrs={'type': 'time'})
        }