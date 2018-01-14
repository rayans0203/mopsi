from django.shortcuts import render,loader
from django.http import HttpResponse
from . import mlmc
import json

# Create your views here.
def home(request):

	return  render(request,'userInterface/home.html')

def pricer(request):

	return render(request,'userInterface/pricer.html')

def contact(request):

	return render(request,'userInterface/contact.html')

def computation(request):
	# lorsque l'on clique sur le bouton Calculate, on effectue le calcul

	# J ai retourné une HttpResponse en me basant sur la source suivante:
	# https://stackoverflow.com/questions/37998675/django-run-python-script-and-pass-output-to-javascript-file

	# pour l instant, je ne prends pas en compte les inputs de l'utilisateur
	o=mlmc.optionPricer(100,100,0.2,3,"BS","E",kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)
	payoff,time_=o.price(method="bs")

	# on envoie payoff, dans computation.html, on le récupère la-bas en écrivant
	# {{payoff}}. Idem avec {{time}}
	#template=loader.get_template('userInterface/computation.html')
	context={'payoff':round(payoff,2),'time':round(time_,2)}

	return HttpResponse(json.dumps(context))
