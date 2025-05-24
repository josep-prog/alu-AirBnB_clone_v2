#!/usr/bin/python3
"""This module defines a class to manage city objects"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from os import getenv

class City(BaseModel, Base):
    """This class manages city objects"""
    __tablename__ = 'cities'
    
    name = Column(String(128), nullable=False)
    state_id = Column(String(60), ForeignKey('states.id'), nullable=False)
    
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        places = relationship("Place", backref="city", cascade="all, delete-orphan")
