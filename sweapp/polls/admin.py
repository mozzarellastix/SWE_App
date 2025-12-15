from django.contrib import admin
from .models import UserProfile, Group, GroupMembership, Post, Message, Event, EventRSVP, Friendship

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(GroupMembership)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Event)
admin.site.register(EventRSVP)
admin.site.register(Friendship)