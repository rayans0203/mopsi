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

	o=mlmc.optionPricer(100,100,0.2,3,"BS",kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)
	call,time_call=o.price("call","bs")
	put,time_put=o.price("put","bs")

	context={'call':round(call,2),'put':round(put,2)}

	return HttpResponse(json.dumps(context))