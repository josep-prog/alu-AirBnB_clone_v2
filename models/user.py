#!/usr/bin/python3
"""User class definition"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from os import getenv

class User(BaseModel, Base):
    """User class for storing user information"""
    __tablename__ = 'users'
    
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        places = relationship('Place', backref='user', cascade='all, delete-orphan')
        reviews = relationship('Review', backref='user', cascade='all, delete-orphan')
