from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from ..database import Base
from sqlalchemy.orm import relationship


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    plan_products = relationship(
        "PlanProduct",
        back_populates="tool",
        cascade="all, delete-orphan"
    )

    endpoints = relationship(
        "Endpoint",
        back_populates="tool",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tool {self.slug}>"
    
class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(String, primary_key=True)
    tool_id = Column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    path = Column(String, nullable=False)

    tool = relationship("Tool", back_populates="endpoints")

    __table_args__ = (
        UniqueConstraint("tool_id", "path", name="unique_tool_path"),
    )
