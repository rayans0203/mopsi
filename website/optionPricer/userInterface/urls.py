from django.conf.urls import url,include
from . import views

urlpatterns = [
	url(r'home$',views.home,name='home'),
	url(r'pricer$',views.pricer,name='pricer'),
	url(r'contact$',views.contact,name='contact'),
	url(r'computation$',views.computation,name='computation'),
]