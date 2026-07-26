from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    photo_url = Column(String, nullable=True)
    behavior_notes = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)

class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True, index=True)
    pet_token = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    captured = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
