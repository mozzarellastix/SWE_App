from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    major = models.CharField(max_length=100, blank=True, default='')
    birthday = models.DateField(null=True, blank=True)
    year = models.CharField(max_length=20, blank=True, default='')
    workplace = models.CharField(max_length=200, blank=True, default='')
    hometown = models.CharField(max_length=200, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Group(models.Model):
    """Represents a club or study group"""
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='user_groups', through='GroupMembership')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Junction table for User-Group many-to-many relationship"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'group')
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Post(models.Model):
    """Represents a post created by a user"""
    post_id = models.AutoField(primary_key=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Post by {self.created_by.username} at {self.timestamp}"


class Message(models.Model):
    """Represents a message sent between users"""
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Event(models.Model):
    """Represents an event hosted by either a user or a group"""
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, default='')
    hosted_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_events', null=True, blank=True)
    hosted_by_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='hosted_events', null=True, blank=True)
    attendees = models.ManyToManyField(User, related_name='attending_events', through='EventRSVP', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        host = self.hosted_by_user.username if self.hosted_by_user else self.hosted_by_group.name
        return f"{self.title} hosted by {host}"


class EventRSVP(models.Model):
    """Tracks user RSVPs for events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rsvp_status = models.CharField(max_length=20, choices=[
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('not_going', 'Not Going')
    ], default='going')
    rsvp_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}: {self.rsvp_status}"


class Friendship(models.Model):
    """Tracks friendships between users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'friend')
    
    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}: {self.status}"
