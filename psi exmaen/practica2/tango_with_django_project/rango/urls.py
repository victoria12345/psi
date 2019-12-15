import django.urls
from rango import views

app_name = 'rango'

urlpatterns = [
    django.urls.path('', views.index, name='index'),
    django.urls.path('about/', views.about, name='about'),
    django.urls.path('category/<slug:category_name_slug>/',
                     views.show_category, name='show_category'),
    django.urls.path('add_category/', views.add_category, name='add_category'),
    django.urls.path('category/<slug:category_name_slug>/add_page/',
                     views.add_page, name='add_page'),
    django.urls.path('register/', views.register, name='register'),
    django.urls.path('login/', views.user_login, name='login'),
    django.urls.path('restricted/', views.restricted, name='restricted'),
    django.urls.path('logout/', views.user_logout, name='logout'),
]
