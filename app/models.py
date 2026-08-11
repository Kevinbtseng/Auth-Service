from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    time_created = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  