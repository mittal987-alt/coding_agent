from backend.app.events.logger import console_logger
class WebSocketManager:

    def __init__(self):

        self.connections = []

    async def connect(self, websocket):

        await websocket.accept()

        self.connections.append(websocket)

    async def disconnect(self, websocket):

        self.connections.remove(websocket)

    async def broadcast(

        self,

        event,

    ):

        for ws in self.connections:

            await ws.send_json(

                event.model_dump()

            )

        dispatcher = EventDispatcher()

         dispatcher.subscribe(

         console_logger,

        )

         dispatcher.subscribe(

          websocket_manager.broadcast,

         )