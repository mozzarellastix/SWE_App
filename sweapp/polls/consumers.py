"""
WebSocket Consumer for Real-Time Chat

A Consumer is like a Django view, but for WebSocket connections.
It handles:
1. Connection establishment (when user opens chat)
2. Receiving messages from the client (browser)
3. Sending messages to the client
4. Disconnection cleanup
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles real-time chat between two users.
    
    How it works:
    1. When a user opens a chat with someone, they connect via WebSocket
    2. Both users join a shared "room" (like a chat room)
    3. When either sends a message, it's broadcast to everyone in the room
    4. The message is also saved to the database
    """
    
    async def connect(self):
        """
        Called when the WebSocket connection is established.
        This happens when a user opens the chat page.
        """
        # Get the current user (available because of AuthMiddlewareStack)
        self.user = self.scope['user']
        
        # Get the other user's ID from the URL (we'll set this up in routing)
        # Example: ws://localhost:8000/ws/chat/5/ means chatting with user 5
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        
        # Create a unique room name for these two users
        # We sort the IDs so user1+user2 and user2+user1 join the same room
        user_ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join the room (channel layer handles this)
        # Now this connection will receive all messages sent to this room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        print(f"[WebSocket] User {self.user.username} connected to room {self.room_name}")
    
    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.
        This happens when user closes the browser or navigates away.
        """
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print(f"[WebSocket] User {self.user.username} disconnected from room {self.room_name}")
    
    async def receive(self, text_data):
        """
        Called when we receive a message from the client (browser).
        This happens when a user types a message and clicks Send.
        """
        # Parse the JSON message from the browser
        data = json.loads(text_data)
        message_content = data['message']
        receiver_id = data['receiver_id']
        
        print(f"[WebSocket] Received message from {self.user.username}: {message_content}")
        
        # Save the message to the database
        message = await self.save_message(
            sender=self.user,
            receiver_id=receiver_id,
            content=message_content
        )
        
        # Broadcast the message to everyone in the room
        # This will trigger the chat_message() method below
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # This calls the chat_message method
                'message': message_content,
                'sender_username': self.user.username,
                'sender_id': self.user.id,
                'timestamp': message.timestamp.strftime('%b %d, %I:%M %p')
            }
        )
    
    async def chat_message(self, event):
        """
        Called when a message is broadcast to the room.
        This sends the message to the client (browser).
        """
        # Send the message to the WebSocket (to the browser)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_username': event['sender_username'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def save_message(self, sender, receiver_id, content):
        """
        Save the message to the database.
        We use @database_sync_to_async because Django ORM is synchronous
        but our Consumer is asynchronous.
        
        We import models here (not at top) to avoid Django setup issues.
        """
        from django.contrib.auth.models import User
        from .models import Message
        
        receiver = User.objects.get(id=receiver_id)
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        return message
