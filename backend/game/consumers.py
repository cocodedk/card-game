import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Don't import User directly at module level
# from django.contrib.auth.models import User

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        data = text_data_json.get('data', {})

        # Process different game actions
        if action == 'play_card':
            # Process card play logic
            await self.process_play_card(data)
        elif action == 'draw_card':
            # Process card draw logic
            await self.process_draw_card(data)
        elif action == 'end_turn':
            # Process end turn logic
            await self.process_end_turn(data)
        elif action == 'join_game':
            # Process player joining game
            await self.process_join_game(data)

    async def process_play_card(self, data):
        # This will be implemented with game logic
        # For now, just broadcast the action
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_action',
                'action': 'play_card',
                'player': data.get('player'),
                'card': data.get('card')
            }
        )

    async def process_draw_card(self, data):
        # This will be implemented with game logic
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_action',
                'action': 'draw_card',
                'player': data.get('player')
            }
        )

    async def process_end_turn(self, data):
        # This will be implemented with game logic
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_action',
                'action': 'end_turn',
                'player': data.get('player')
            }
        )

    async def process_join_game(self, data):
        # This will be implemented with game logic
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_action',
                'action': 'join_game',
                'player': data.get('player')
            }
        )

    # Receive message from game group
    async def game_action(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    # Use lazy imports for Django models when needed
    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth.models import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
