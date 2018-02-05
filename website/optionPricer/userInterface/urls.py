from django.views.generic import ListView, DetailView
from . import models
from django.conf.urls import url,include
from . import views

urlpatterns = [
	url(r'home/$',views.home,name='home'),
	url(r'pricer/$',views.pricer,name='pricer'),
	url(r'resources$',views.resources,name='resources'),
	url(r'computation/'+r'([0-9]*[.]?[0-9]+)/'*5+r'(\w+)/'*3,views.computation,name="computation"),
	url(r'faq/$',ListView.as_view(queryset=models.Post.objects.all(),
		template_name="userInterface/faq.html")),
]