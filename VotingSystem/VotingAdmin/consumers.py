from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ElectionResultsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("election_results", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("election_results", self.channel_name)

    async def receive_json(self, content):
        # Process the vote and broadcast the update
        pass

    async def election_results_update(self, event):
        await self.send_json(event["text"])