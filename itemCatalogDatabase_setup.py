#!/usr/bin/python3

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable = False)
    permission = relationship('Permission')

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key = True)
    level = Column(String(20), nullable = False)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    user = relationship('User')

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key = True)
    name = Column(String(30), nullable = False)
    description = Column(String(300), nullable = False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable = False)
    category = relationship('Category')
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    user = relationship('User')

class Favorite(Base):
    __tablename__ = 'favorites'
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False, primary_key = True)
    user = relationship('User')
    item_id = Column(Integer, ForeignKey('items.id'), nullable = False, primary_key = True)
    item = relationship('Item')

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)