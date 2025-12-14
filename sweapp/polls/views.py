from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.db.models import Q
from .models import Message

def index(request):
    return HttpResponse("Hello world. You're at the polls index.")

def login_view(request):
    # If user is already logged in, redirect to feed
    if request.user.is_authenticated:
        return redirect('/polls/feed/')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"[LOGIN] Attempting login for email: {email}")
        
        # Django's authenticate() uses username by default, but we can use email
        # First, try to find user by email
        from django.contrib.auth.models import User
        try:
            # Use filter().first() instead of get() to handle multiple users with same email
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                raise User.DoesNotExist
            username = user_obj.username
            print(f"[LOGIN] Found user: {username}")
        except User.DoesNotExist:
            print(f"[LOGIN] No user found with email: {email}")
            messages.error(request, 'Invalid email or password.')
            return render(request, 'main/login.html')
        
        # Authenticate user against database
        user = authenticate(request, username=username, password=password)
        print(f"[LOGIN] Authentication result: {user}")
        
        if user is not None:
            # Login successful - log the user in
            login(request, user)
            print(f"[LOGIN] User logged in successfully. Authenticated: {request.user.is_authenticated}")
            return redirect('/polls/feed/')  # Redirect to feed page after login
        else:
            # Login failed
            print(f"[LOGIN] Authentication failed for user: {username}")
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'main/login.html')

def feed_view(request):
    print(f"[FEED] User: {request.user}, Authenticated: {request.user.is_authenticated}")
    
    # Check if user is logged in
    if not request.user.is_authenticated:
        print(f"[FEED] User not authenticated, redirecting to login")
        return redirect('/')  # Redirect to login page
    
    # Handle post creation
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            from .models import Post
            Post.objects.create(
                content=content,
                created_by=request.user
            )
            return redirect('feed')
    
    # Get all posts
    from .models import Post, Event
    posts = Post.objects.all().order_by('-timestamp')[:50]
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
    
    print(f"[FEED] Rendering feed for user: {request.user.username}")
    context = {
        'posts': posts,
        'events': events,
    }
    return render(request, 'main/feed.html', context)

def events_view(request):
    return render(request, 'main/events.html')

def messages_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    users = User.objects.exclude(id=request.user.id)
    
    conversation_with = None  
    conversation_messages = []  
    
    if 'user_id' in request.GET:
        try:
            conversation_with = User.objects.get(id=request.GET['user_id'])
            
            conversation_messages = Message.objects.filter(
                Q(sender=request.user, receiver=conversation_with) |
                Q(sender=conversation_with, receiver=request.user)
            ).order_by('timestamp') 
            
            Message.objects.filter(
                sender=conversation_with,
                receiver=request.user,
                is_read=False
            ).update(is_read=True)
            
        except User.DoesNotExist:
            pass 
    
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        
        if receiver_id and content:
            try:
                receiver = User.objects.get(id=receiver_id)

                Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content
                )

                return redirect(f'/polls/messages/?user_id={receiver_id}')
            except User.DoesNotExist:
                pass
    
    context = {
        'users': users,  
        'conversation_with': conversation_with, 
        'conversation_messages': conversation_messages,  
    }
    
    return render(request, 'main/messages.html', context)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Post, Group, Event, UserProfile
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's posts
    user_posts = Post.objects.filter(created_by=request.user).order_by('-timestamp')
    
    # Get user's groups
    user_groups = request.user.user_groups.all()
    
    # Get upcoming events (user's or their groups')
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now()
    ).filter(
        models.Q(hosted_by_user=request.user) | 
        models.Q(hosted_by_group__in=user_groups)
    ).order_by('date')[:5]
    
    context = {
        'user_posts': user_posts,
        'user_groups': user_groups,
        'upcoming_events': upcoming_events,
        'profile': profile,
    }
    return render(request, 'main/profile.html', context)

def navbar(request): # do we need a view for navbar?
    return HttpResponse("This is the navbar component.")

def logout_view(request):
    print(f"[LOGOUT] User {request.user.username} logging out")
    logout(request)
    print(f"[LOGOUT] User logged out. Authenticated: {request.user.is_authenticated}")
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

def sign_up(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'main/signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/signup.html')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, 'Account created! You can now log in.')
        return redirect('login')  
    
    return render(request, 'main/signup.html')