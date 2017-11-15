from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
	text = """ <h1> Bienvenue sur mon site ! </h1>
				<p> Ceci deviendra un pricer d'options bientôt ! </p>"""
	return HttpResponse(text)