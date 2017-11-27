from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):

	return  render(request,'userInterface/home.html')

def pricer(request):

	return render(request,'userInterface/pricer.html')

def contact(request):

	return render(request,'userInterface/contact.html')