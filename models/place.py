#!/usr/bin/python3
"""Place class definition"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from os import getenv

# Association table for many-to-many relationship between Place and Amenity
place_amenity = Table('place_amenity', Base.metadata,
    Column('place_id', String(60), ForeignKey('places.id'), primary_key=True, nullable=False),
    Column('amenity_id', String(60), ForeignKey('amenities.id'), primary_key=True, nullable=False)
)

class Place(BaseModel, Base):
    """Place class for storing place information"""
    __tablename__ = 'places'
    
    city_id = Column(String(60), ForeignKey('cities.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    number_rooms = Column(Integer, nullable=False, default=0)
    number_bathrooms = Column(Integer, nullable=False, default=0)
    max_guest = Column(Integer, nullable=False, default=0)
    price_by_night = Column(Integer, nullable=False, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationships for DBStorage
    if getenv('HBNB_TYPE_STORAGE') == 'db':
        user = relationship("User", backref="places", viewonly=True)
        city = relationship("City", backref="places", viewonly=True)
        reviews = relationship('Review', backref='place', cascade='all, delete-orphan')
        amenities = relationship('Amenity', secondary=place_amenity, viewonly=False)
    else:
        @property
        def reviews(self):
            """Getter for reviews"""
            from models import storage
            from models.review import Review
            review_list = []
            for review in storage.all(Review).values():
                if review.place_id == self.id:
                    review_list.append(review)
            return review_list
        
        @property
        def amenities(self):
            """Getter for amenities"""
            from models import storage
            from models.amenity import Amenity
            amenity_list = []
            for amenity in storage.all(Amenity).values():
                if amenity.id in self.amenity_ids:
                    amenity_list.append(amenity)
            return amenity_list
        
        @amenities.setter
        def amenities(self, obj):
            """Setter for amenities"""
            from models.amenity import Amenity
            if isinstance(obj, Amenity):
                if not hasattr(self, 'amenity_ids'):
                    self.amenity_ids = []
                if obj.id not in self.amenity_ids:
                    self.amenity_ids.append(obj.id)
