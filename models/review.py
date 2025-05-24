#!/usr/bin/python3
"""Review class definition"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

class Review(BaseModel, Base):
    """Review class for storing review information"""
    __tablename__ = 'reviews'
    
    text = Column(String(1024), nullable=False)
    place_id = Column(String(60), ForeignKey('places.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
