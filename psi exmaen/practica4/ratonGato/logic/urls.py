"""
    urls logic
"""
from django.urls import path

# from datamodel import views
from logic import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('counter/', views.counter, name='counter'),
    path('create_game/', views.create_game, name='create_game'),
    path('join_game/', views.join_game, name='join_game'),
    path('select_game/<str:method>', views.select_game, name='select_game'),
    path('select_game/<str:method>/<int:game_id>', views.select_game, name='select_game'),
    path('show_game/', views.show_game, name='show_game'),
    path('move/', views.move, name='move'),
    path('replay_game/', views.replay_game, name='replay_game'),
    path('get_move/', views.get_move, name='get_move'),
    path('get_game_status/', views.get_game_status, name='get_game_status'),
    path('is_it_my_turn/', views.is_it_my_turn, name='is_it_my_turn'),
]
