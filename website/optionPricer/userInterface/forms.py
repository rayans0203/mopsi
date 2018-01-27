# https://openclassrooms.com/courses/developpez-votre-site-web-avec-le-framework-django/les-formulaires-6#_=_"3
from django import forms

class pricingForm(forms.Form):
    Stock = forms.IntegerField(min_value=0)
    Order_list = (('1', 'Call',), ('2', 'Put',))
    Order = forms.ChoiceField(widget=forms.RadioSelect, choices=Order_list)
    Model_list = (('1', 'Modèle 1',), ('2', 'Modèle 2',))
    Model = forms.ChoiceField(widget=forms.RadioSelect, choices=Model_list)
    Strike = forms.IntegerField(min_value=0)
    Maturity = forms.IntegerField(min_value=0)
    Volatility = forms.IntegerField(min_value=0)
    Number = forms.IntegerField(min_value=0)
    Interest = forms.IntegerField(min_value=0)
    
class resultForm(forms.Form):
    price= forms.CharField(max_length=100)