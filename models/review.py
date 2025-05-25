#!/usr/bin/python3
"""This module defines a class to manage review objects"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from os import getenv

class Review(BaseModel, Base):
    """This class manages review objects"""
    __tablename__ = 'reviews'
    
    text = Column(String(1024), nullable=False)
    place_id = Column(String(60), ForeignKey('places.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        place = relationship('Place', backref='reviews', cascade='all, delete-orphan')
        user = relationship('User', backref='reviews', cascade='all, delete-orphan')
