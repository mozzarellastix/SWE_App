from django.urls import path
from . import views

# urlpatterns = [
#     path("", views.index, name="index"),
# ]


urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('feed/', views.feed_view, name='feed-page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('events/', views.events_view, name='events'),
    path('create_event/', views.create_event_view, name='create_event'),
    path('event/<int:event_id>/rsvp/', views.event_rsvp, name='event_rsvp'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('messages/', views.messages_view, name='messages'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('friend/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend/respond/<int:friendship_id>/<str:action>/', views.respond_friend_request, name='respond_friend_request'),
]