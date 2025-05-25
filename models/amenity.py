#!/usr/bin/python3
"""This module defines a class to manage amenity objects"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from os import getenv

class Amenity(BaseModel, Base):
    """This class manages amenity objects"""
    __tablename__ = 'amenities'
    
    name = Column(String(128), nullable=False)
    
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        place_amenities = relationship('Place', secondary='place_amenity',
                                     back_populates='amenities')
    else:
        @property
        def place_amenities(self):
            """Getter for place_amenities"""
            from models import storage
            from models.place import Place
            place_list = []
            for place in storage.all(Place).values():
                if self.id in place.amenity_ids:
                    place_list.append(place)
            return place_list
