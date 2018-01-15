from django.conf.urls import url,include
from . import views
from django.views.generic import ListView, DetailView
from . import models

urlpatterns = [
	url(r'home/$',views.home,name='home'),
	url(r'pricer/$',views.pricer,name='pricer'),
	url(r'contact/$',views.contact,name='contact'),
	url(r'computation/$',views.computation,name='computation'),
	url(r'faq/$',ListView.as_view(queryset=models.Post.objects.all(),
		template_name="userInterface/faq.html")),
	# url(r'(?P<pk>\d+)$',DetailView.as_view(model=models.Post,
	# 	template_name='userInterface/post.html'))
]