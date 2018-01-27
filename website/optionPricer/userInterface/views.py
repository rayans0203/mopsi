from django.shortcuts import render,loader
from django.http import HttpResponse
from .forms import pricingForm, resultForm
from . import mlmc
import json

# Create your views here.
def home(request):
	return  render(request,'userInterface/home.html')

# https://openclassrooms.com/courses/developpez-votre-site-web-avec-le-framework-django/les-formulaires-6#_=_
def pricer(request):
	form = pricingForm(request.POST or None)
	
	if form.is_valid(): 
		Stock = form.cleaned_data['Stock']
		Model = form.cleaned_data['Model']
		Strike = form.cleaned_data['Strike']
		Maturity = form.cleaned_data['Maturity']
		Volatility = form.cleaned_data['Volatility']
		Number = form.cleaned_data['Number']
		Interest = form.cleaned_data['Interest']		
		o=mlmc.optionPricer(int(Stock),100,0.2,3,"BS","E",kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)
		payoff,time=o.price(method="bs")
				
	return render(request,'userInterface/pricer.html', locals())

def contact(request):
	return render(request,'userInterface/contact.html')
	
