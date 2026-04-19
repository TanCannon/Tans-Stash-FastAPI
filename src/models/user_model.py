from sqlachemy import Column, Integer, String
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="user")
    password_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"