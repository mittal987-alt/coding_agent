from sqlalchemy.event import dispatcher
from __future__ import annotations

from app.events.models import WorkflowEvent


class EventDispatcher:

    def __init__(self):

        self.subscribers = []

    def subscribe(self, callback):

        self.subscribers.append(callback)

    async def publish(

        self,

        event: WorkflowEvent,

    ):

        for subscriber in self.subscribers:

            await subscriber(event)

        await dispatcher.publish(

            WorkflowEvent(  

                workflow_id=state.workflow_id,

                event=EventType.AGENT_STARTED,

                agent=self.name,

        message=f"{self.name} started",

        timestamp=datetime.utcnow(),

       )

     )


     await dispatcher.publish(

    WorkflowEvent(

        workflow_id=state.workflow_id,

        event=EventType.AGENT_FINISHED,

        agent=self.name,

        message=f"{self.name} finished",

        timestamp=datetime.utcnow(),

    )

)