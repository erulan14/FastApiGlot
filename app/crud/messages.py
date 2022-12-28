from ..db.mongodb import AsyncIOMotorClient
from ..core.config import database_name_messages
from ..models.messages import MessageInDB


async def get_messages_by_id(id: int, conn: AsyncIOMotorClient, limit=20, from_time=0, to_time=0) -> list[MessageInDB]:
    messages: list[MessageInDB] = []
    messages_docs = conn[database_name_messages][str(id)].find({"t": {"$gte": from_time, "$lte": to_time}}, limit=limit).sort("t", 1)
    print(messages_docs.to_list(length=limit))

    async for row in messages_docs:
        messages.append(
            MessageInDB(**row)
        )
    return messages