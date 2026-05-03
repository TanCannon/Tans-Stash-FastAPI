from typing import List
from datetime import datetime
from pydantic import BaseModel, condecimal, ConfigDict

class PlanBase(BaseModel):
    name: str
    price: condecimal(max_digits=10, decimal_places=2)
    request_limit:  int
    rate_limit: int
    tool_ids: List[int]
     
class PlanCreate(PlanBase):
    model_config = ConfigDict(from_attributes=True)

class PlanResponse(PlanBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# for pagination of the posts
class PaginatedPlans(BaseModel):
    items: List[PlanResponse]
    total: int
    skip: int
    limit: int
