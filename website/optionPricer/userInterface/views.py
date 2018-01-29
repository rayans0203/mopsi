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

def computation(request,S0,K,sigma,T,r,Model,Type,Method):
	# lorsque l'on clique sur le bouton Calculate, on effectue le calcul
	S0=float(S0)
	K=float(K)
	sigma=float(sigma)
	T=float(T)
	r=float(r)

	o=mlmc.optionPricer(S0,K,sigma,T,Model,Type,r=r,kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)
	call,time_call=o.price("bs")
	put,time_put=o.price("bs")

	# rajouter le calcul du delta, gamma et intervalle de confiance

	context={'call':round(call,2),'put':round(put,2)}

	return HttpResponse(json.dumps(context))


def resources(request):
	return render(request,'userInterface/resources.html')
	
