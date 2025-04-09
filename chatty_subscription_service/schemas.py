from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    following_id: int
