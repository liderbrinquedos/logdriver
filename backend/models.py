from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="motorista")  # admin, motorista
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deliveries = relationship("Delivery", back_populates="owner")


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    nrunico = Column(Integer, nullable=True, index=True)
    nf_number = Column(String, index=True, nullable=False)
    client = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    driver = Column(String, nullable=True)
    company = Column(String, nullable=True)
    observations = Column(Text, nullable=True)
    canhoto_path = Column(String, nullable=True)
    status = Column(String, default="pendente", index=True)
    delivery_canhoto_path = Column(String, nullable=True)
    delivery_observations = Column(Text, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    owner = relationship("User", back_populates="deliveries")
