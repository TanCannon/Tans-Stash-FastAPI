from sqlalchemy import Column, Integer, String, Text
from ..database import Base  # adjust to your project name


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Tool {self.slug}>"
