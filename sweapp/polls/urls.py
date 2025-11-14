from django.urls import path
from . import views

# urlpatterns = [
#     path("", views.index, name="index"),
# ]

# testing out views - ash
urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('feed/', views.feed_view, name='feed-page'),  # Added explicit feed URL
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('events/', views.events_view, name='events'),
    path('messages/', views.messages_view, name='messages'),
    path('profile/', views.profile_view, name='profile')
    # path('navbar/', views.navbar, name='navbar'),
]