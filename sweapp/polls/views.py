from django.http import HttpResponse

from django.shortcuts import render

def index(request):
    return HttpResponse("Hello world. You're at the polls index.")

# Create your views here.

# testing out views.. - ash
# unless its supposed to be (for example)'main/login.html' <- it was lmao
def login_view(request):
    return render(request, 'main/login.html')

def feed_view(request):
    return render(request, 'main/feed.html')

def events_view(request):
    return render(request, 'main/events.html')

def messages_view(request): 
    return render(request, 'main/messages.html')

def profile_view(request):
    return render(request, 'main/profile.html')

def navbar(request): # do we need a view for navbar?
    return HttpResponse("This is the navbar component.")
