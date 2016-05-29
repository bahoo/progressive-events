from django import forms


class SearchForm(forms.Form):
    distance = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'hidden'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'hidden'}))
    days = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'hidden'}))