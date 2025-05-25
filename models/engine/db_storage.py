#!/usr/bin/python3
"""This module defines a class to manage database storage for hbnb clone"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity


class DBStorage:
    """This class manages storage of hbnb models in MySQL database"""
    __engine = None
    __session = None

    def __init__(self):
        """Initialize DBStorage"""
        user = os.getenv('HBNB_MYSQL_USER')
        pwd = os.getenv('HBNB_MYSQL_PWD')
        host = os.getenv('HBNB_MYSQL_HOST')
        db = os.getenv('HBNB_MYSQL_DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.format(user, pwd, host, db), pool_pre_ping=True)
        if os.getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Query on the current database session all objects depending of the class name"""
        classes = {
            'State': State, 'City': City, 'User': User,
            'Place': Place, 'Review': Review, 'Amenity': Amenity
        }
        result = {}
        if cls is not None:
            if type(cls) is str:
                cls = classes[cls]
            for obj in self.__session.query(cls).all():
                key = obj.__class__.__name__ + '.' + obj.id
                result[key] = obj
        else:
            for cls_name, cls_obj in classes.items():
                for obj in self.__session.query(cls_obj).all():
                    key = obj.__class__.__name__ + '.' + obj.id
                    result[key] = obj
        return result

    def new(self, obj):
        """Add the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """Commit all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create all tables in the database and create the current database session"""
        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(session_factory)
        self.__session = Session()

    def close(self):
        """Close the current database session"""
        self.__session.close()

    def get(self, cls, id):
        """Retrieve one object based on class name and ID"""
        if cls is None or id is None:
            return None
        if type(cls) is str:
            cls = eval(cls)
        return self.__session.query(cls).filter(cls.id == id).first()

    def count(self, cls=None):
        """Count the number of objects in storage"""
        if cls is None:
            total = 0
            total += self.__session.query(State).count()
            total += self.__session.query(City).count()
            total += self.__session.query(User).count()
            total += self.__session.query(Place).count()
            total += self.__session.query(Review).count()
            total += self.__session.query(Amenity).count()
            return total
        if type(cls) is str:
            cls = eval(cls)
        return self.__session.query(cls).count() 