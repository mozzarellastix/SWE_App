from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Event
from django.utils import timezone
from django.db import models
from django.db.models import Q
from .models import Message

def index(request):
    return HttpResponse("Hello world. You're at the polls index.")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/polls/feed/')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"[LOGIN] Attempting login for email: {email}")
        
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                raise User.DoesNotExist
            username = user_obj.username
            print(f"[LOGIN] Found user: {username}")
        except User.DoesNotExist:
            print(f"[LOGIN] No user found with email: {email}")
            messages.error(request, 'Invalid email or password.')
            return render(request, 'main/login.html')
        
        user = authenticate(request, username=username, password=password)
        print(f"[LOGIN] Authentication result: {user}")
        
        if user is not None:
            login(request, user)
            print(f"[LOGIN] User logged in successfully. Authenticated: {request.user.is_authenticated}")
            return redirect('/polls/feed/')
        else:
            print(f"[LOGIN] Authentication failed for user: {username}")
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'main/login.html')

def feed_view(request):
    print(f"[FEED] User: {request.user}, Authenticated: {request.user.is_authenticated}")
    
    if not request.user.is_authenticated:
        print(f"[FEED] User not authenticated, redirecting to login")
        return redirect('/')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            from .models import Post
            Post.objects.create(
                content=content,
                created_by=request.user
            )
            return redirect('feed')
    
    from .models import Post, Event, EventRSVP
    posts = Post.objects.all().order_by('-timestamp')[:50]
    
    hosted_events = Event.objects.filter(
        date__gte=timezone.now(),
        hosted_by_user=request.user
    ).order_by('date')[:3]
    
    attending_event_ids = EventRSVP.objects.filter(
        user=request.user,
        rsvp_status='going'
    ).values_list('event_id', flat=True)
    
    attending_events = Event.objects.filter(
        date__gte=timezone.now(),
        event_id__in=attending_event_ids
    ).exclude(hosted_by_user=request.user).order_by('date')[:3]
    
    all_user_events = list(hosted_events) + list(attending_events)
    all_user_events.sort(key=lambda e: e.date)
    
    print(f"[FEED] Rendering feed for user: {request.user.username}")
    print(f"[FEED] Hosted events: {len(hosted_events)}, Attending events: {len(attending_events)}")
    context = {
        'posts': posts,
        'events': all_user_events[:3],
    }
    return render(request, 'main/feed.html', context)

def events_view(request):
    from .models import EventRSVP
    
    events = Event.objects.all().order_by('date')
    
    user_rsvps = {}
    if request.user.is_authenticated:
        rsvps = EventRSVP.objects.filter(user=request.user)
        user_rsvps = {rsvp.event_id: rsvp.rsvp_status for rsvp in rsvps}
    
    events_with_data = []
    for event in events:
        rsvp_count = EventRSVP.objects.filter(event=event, rsvp_status='going').count()
        events_with_data.append({
            'event': event,
            'rsvp_count': rsvp_count,
            'user_rsvp': user_rsvps.get(event.event_id)
        })
    
    context = {
        'events_with_data': events_with_data,
        'events': events,
    }
    return render(request, 'main/events.html', context)

def create_event_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        date = request.POST.get("date")
        description = request.POST.get("description")
        location = request.POST.get("location")
        
        event = Event(
            title=title,
            date=date,
            description=description,
            hosted_by_user=request.user,
        )
        event.save()
        return redirect('/polls/events/')
    return render(request, 'main/create_event.html')

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
    
    from .models import Post, Group, Event, UserProfile, Friendship, EventRSVP
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    user_posts = Post.objects.filter(created_by=request.user).order_by('-timestamp')
    
    user_groups = request.user.user_groups.all()
    
    friend_count = Friendship.objects.filter(
        user=request.user,
        status='accepted'
    ).count()
    
    pending_requests = Friendship.objects.filter(
        friend=request.user,
        status='pending'
    )
    
    hosted_events = Event.objects.filter(
        date__gte=timezone.now(),
        hosted_by_user=request.user
    ).order_by('date')[:5]
    
    print(f"[PROFILE] Hosted events count: {hosted_events.count()}")
    for evt in hosted_events:
        print(f"[PROFILE] Hosted: {evt.title} on {evt.date}")
    
    attending_event_ids = EventRSVP.objects.filter(
        user=request.user,
        rsvp_status='going'
    ).values_list('event_id', flat=True)
    
    print(f"[PROFILE] Attending event IDs: {list(attending_event_ids)}")
    
    attending_events = Event.objects.filter(
        date__gte=timezone.now(),
        event_id__in=attending_event_ids
    ).exclude(hosted_by_user=request.user).order_by('date')[:5]
    
    print(f"[PROFILE] Attending events count: {attending_events.count()}")
    for evt in attending_events:
        print(f"[PROFILE] Attending: {evt.title} on {evt.date}")
    
    context = {
        'user_posts': user_posts,
        'user_groups': user_groups,
        'hosted_events': hosted_events,
        'attending_events': attending_events,
        'profile': profile,
        'friend_count': friend_count,
        'pending_requests': pending_requests,
        'is_own_profile': True,
    }
    return render(request, 'main/profile.html', context)

def navbar(request):
    return HttpResponse("This is the navbar component.")

def logout_view(request):
    print(f"[LOGOUT] User {request.user.username} logging out")
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    print(f"[LOGOUT] User logged out. Authenticated: {request.user.is_authenticated}")
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


def delete_event(request, event_id):
    """Delete an event (only by host)"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        event = Event.objects.get(event_id=event_id)
        
        if event.hosted_by_user == request.user:
            event.delete()
            messages.success(request, 'Event deleted successfully!')
        else:
            messages.error(request, 'You can only delete events you host!')
    except Event.DoesNotExist:
        messages.error(request, 'Event not found!')
    
    return redirect('events')

def event_rsvp(request, event_id):
    """Handle RSVP for an event"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import EventRSVP
    
    try:
        event = Event.objects.get(event_id=event_id)
        
        if request.method == 'POST':
            status = request.POST.get('status', 'going')
            
            rsvp, created = EventRSVP.objects.get_or_create(
                user=request.user,
                event=event,
                defaults={'rsvp_status': status}
            )
            
            if not created:
                rsvp.rsvp_status = status
                rsvp.save()
        
    except Event.DoesNotExist:
        messages.error(request, 'Event not found.')
    
    return redirect('events')


def edit_profile(request):
    """Edit user profile"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import UserProfile
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        
        profile.bio = request.POST.get('bio', '')
        profile.major = request.POST.get('major', '')
        profile.year = request.POST.get('year', '')
        profile.workplace = request.POST.get('workplace', '')
        profile.hometown = request.POST.get('hometown', '')
        
        birthday = request.POST.get('birthday')
        if birthday:
            from datetime import datetime
            try:
                profile.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
            except:
                pass
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'main/edit_profile.html', context)


def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Friendship
    
    try:
        friend = User.objects.get(id=user_id)
        
        if friend == request.user:
            messages.error(request, "You can't send a friend request to yourself!")
            return redirect('profile')
        
        existing = Friendship.objects.filter(
            Q(user=request.user, friend=friend) |
            Q(user=friend, friend=request.user)
        ).first()
        
        if existing:
            messages.info(request, 'Friend request already sent or you are already friends.')
        else:
            Friendship.objects.create(
                user=request.user,
                friend=friend,
                status='pending'
            )
            messages.success(request, f'Friend request sent to {friend.username}!')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


def respond_friend_request(request, friendship_id, action):
    """Accept or reject a friend request"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Friendship
    
    try:
        friendship = Friendship.objects.get(id=friendship_id, friend=request.user)
        
        if action == 'accept':
            friendship.status = 'accepted'
            friendship.save()
            Friendship.objects.get_or_create(
                user=request.user,
                friend=friendship.user,
                defaults={'status': 'accepted'}
            )
            messages.success(request, f'You are now friends with {friendship.user.username}!')
        elif action == 'reject':
            friendship.status = 'rejected'
            friendship.save()
            messages.info(request, 'Friend request rejected.')
        
    except Friendship.DoesNotExist:
        messages.error(request, 'Friend request not found.')
    
    return redirect('profile')