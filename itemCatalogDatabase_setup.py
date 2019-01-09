#!/usr/bin/python3

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    username = Column(String(30), nullable = False)
    email = Column(String(50), nullable = False)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)
    description = Column(String(300), nullable = False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable = False)
    category = relationship('Category')
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    user = relationship('User')

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)