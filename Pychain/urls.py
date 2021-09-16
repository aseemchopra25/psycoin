"""Pychain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# Importing important views and urls
from django.conf.urls import url 
# Just to be safe
from blockchain import views
from blockchain.views import *
#configuring new API URL endpoints
urlpatterns = [
    path('admin/', admin.site.urls),
    url('^get_chain$', views.get_chain, name = "get_chain"),
    url('^mine_block$', views.mine_block, name = "mine_block"),
    url('^is_valid$', views.is_valid, name = "is_valid"),
    url('^add_transaction$', views.add_transaction, name = 'add_transaction'),
    url('^connect_node$',views.connect_node, name = 'connect_node'),
    url('^replace_chain$', views.replace_chain, name = 'replace_chain'),
]
# Let's run the server 
# To test the server you have to navigate to http://127.0.0.1:8000/mine_block on your browser
# You can use Postman to see relevant requests, but i'm going to use burpsuite as I have Kali and it's preinstalled

# Let's run two different servers at the same time 
