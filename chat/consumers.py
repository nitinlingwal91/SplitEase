# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import Message, GroupChatRoom
# from groups.models import Group, GroupMember
# from django.utils import timezone


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_id = self.scope['url_route']['kwargs']['group_id']
#         self.room_group_name = f'chat_{self.group_id}'
#         self.user = self.scope['user']
        
#         # Check if user is member
#         is_member = await self.check_membership()
        
#         if not is_member:
#             await self.close()
#             return
        
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         await self.accept()
        
#         # Notify others
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'user_join',
#                 'username': self.user.name,
#             }
#         )
    
#     async def disconnect(self, close_code):
#         # Notify others
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'user_leave',
#                 'username': self.user.name,
#             }
#         )
        
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
    
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message_type = data.get('type', 'text')
#         content = data.get('message', '')
        
#         # Save message to database
#         message = await self.save_message(message_type, content)
        
#         # Send to group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message_id': message.message_id,
#                 'username': self.user.name,
#                 'user_id': self.user.user_id,
#                 'content': message.content,
#                 'message_type': message_type,
#                 'timestamp': message.created_at.isoformat(),
#             }
#         )
    
#     async def chat_message(self, event):
#         """Send message to WebSocket"""
#         await self.send(text_data=json.dumps({
#             'type': 'message',
#             'message_id': event['message_id'],
#             'username': event['username'],
#             'user_id': event['user_id'],
#             'content': event['content'],
#             'message_type': event['message_type'],
#             'timestamp': event['timestamp'],
#         }))
    
#     async def user_join(self, event):
#         """Notify user join"""
#         await self.send(text_data=json.dumps({
#             'type': 'user_join',
#             'username': event['username'],
#         }))
    
#     async def user_leave(self, event):
#         """Notify user leave"""
#         await self.send(text_data=json.dumps({
#             'type': 'user_leave',
#             'username': event['username'],
#         }))
    
#     @database_sync_to_async
#     def check_membership(self):
#         try:
#             group = Group.objects.get(group_id=self.group_id)
#             return GroupMember.objects.filter(group=group, user=self.user).exists()
#         except:
#             return False
    
#     @database_sync_to_async
#     def save_message(self, message_type, content):
#         group = Group.objects.get(group_id=self.group_id)
#         message = Message.objects.create(
#             group=group,
#             sender=self.user,
#             message_type=message_type,
#             content=content,
#         )
#         return message


from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))
