import asyncio
import json
from spade.behaviour import TimeoutBehaviour

from .ontology import ACTION, DESTROY, PERFORMATIVE, PERFORMATIVE_INFORM, NAME
from .pack import Pack, PACK_AMMOPACK, PACK_AUTODESTROY_TIMEOUT
from datetime import datetime, timedelta
from spade.message import Message

now = datetime.now


class AmmoPack(Pack):
    async def setup(self):
        self.type = PACK_AMMOPACK
        timeout = now() + timedelta(seconds=PACK_AUTODESTROY_TIMEOUT)
        self.add_behaviour(self.AutoDestroyBehaviour(start_at=timeout))
        await super().setup()

    async def perform_pack_taken(self, content):
        await self.stop()

    class AutoDestroyBehaviour(TimeoutBehaviour):
        async def run(self):
            msg = Message(to=self.agent.manager)
            msg.set_metadata(PERFORMATIVE, PERFORMATIVE_INFORM)
            content = {NAME: self.agent.name, ACTION: DESTROY}
            msg.body = json.dumps(content)
            if self.agent.is_alive():
                await self.send(msg)
            await asyncio.sleep(1)
            await self.agent.stop()
