#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itemCatalogDatabase_setup import User, Permission, Category, Item, Favorite

engine = create_engine('sqlite:///catalog.db')
Session = sessionmaker(bind=engine)

session = Session()

# Create permission levels that will be set for each user. 'Admins' will be able to create Item Categories,
# add, edit and delete any item and will also set user permissions. 'User's will only be able to add, edit and
# delete their own items. 
permission = Permission(level = 'admin')
session.add(permission)
session.commit()

permission = Permission(level='user')
session.add(permission)
session.commit()

# Create a few users. The first one will have 'admin' level permission.
user = User(name = 'Rodrigo', permission_id = 1)
session.add(user)
session.commit()

user = User(name = 'John', permission_id = 2)
session.add(user)
session.commit()

user = User(name = 'Mary', permission_id = 2)
session.add(user)
session.commit()

user = User(name = 'Julie', permission_id = 2)
session.add(user)
session.commit()

# Create item categories.
category = Category(name = 'Consumer Electronics', user_id = 1)
session.add(category)
session.commit()

category = Category(name = 'Toys, Kids, Baby', user_id = 1)
session.add(category)
session.commit()

category = Category(name = 'Jewelry and Watches', user_id = 1)
session.add(category)
session.commit()

category = Category(name = 'Sports and Outdoors', user_id = 1)
session.add(category)
session.commit()

# Create items for each category.
# Category 1 - Consumer Electronics
item = Item(name = 'GTF 18650 Rechargeable Battery', description = '3.7V 18650 9800mAh Capacity Li-ion', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'VOGROUND Wireless Controller', description = 'Sony PS4 Dual Shock Vibration Joystick. Bluetooth Wireless Controller', category_id = 1, user_id = 2)
session.add(item)
session.commit()

item = Item(name = 'Cewaal i7s TWS Bluetooth Earphone', description = 'Stereo Earbud Wireless Headphones With Charging Box Mic For xiaomi All Phone', category_id = 1, user_id = 3)
session.add(item)
session.commit()

item = Item(name = 'Nikon D3400 DSLR Camera', description = '24.2MP - Video - Bluetooth', category_id = 1, user_id = 4)
session.add(item)
session.commit()

# Category 2 - Toys, Kids, Baby
item = Item(name = 'SYMA S8 RC Helicopter', description = 'Remote Control Helicopter Aircraft With Shatter Resistant Light Alloy And Flashing Lights', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'REAKIDS Beanies Baby Hat', description = 'Cute Pompon Winter Children Knitted Hat', category_id = 1, user_id = 2)
session.add(item)
session.commit()

item = Item(name = 'Muti-fuction Baby/Adult Digital Termometer', description = 'Infrared Forehead and Body Thermometer No-contact Gun', category_id = 1, user_id = 3)
session.add(item)
session.commit()

item = Item(name = 'Silicone Training Toothbrush', description = 'BPA Free Banana Shape, Toddler Safe', category_id = 1, user_id = 4)
session.add(item)
session.commit()

# Category 3 - Jewelry and Watches
item = Item(name = 'Vintage Steampunk Retro Watch', description = 'Bronze Pocket Watch, Quartz', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Marvel Avengers Thor\'s Hammer Keychain', description = 'Mjolnir Metal Model Keyring Pendant', category_id = 1, user_id = 2)
session.add(item)
session.commit()

item = Item(name = 'Nature Lapel Pins', description = 'Cactus, Palm Leaves, Plants, Trees, Enamel Brooches', category_id = 1, user_id = 3)
session.add(item)
session.commit()

# Category 4 - Sports and Outdoors
item = Item(name = 'KastKing Spartacus Plus Baitcasting Fishing Reel', description = 'Dual Brake System Reel, 8KG Maximum Drag 11+1 BBs 6.3:1', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Outdoor 3-4 persons automatic speed open tent', description = 'Throwing pop-up windproof waterproof beach camping tent with large inner space', category_id = 1, user_id = 2)
session.add(item)
session.commit()

item = Item(name = 'Silicone Mouthpiece Teeth Protector', description = 'For Boxing, Baseball, Single Side Mouth Guard', category_id = 1, user_id = 3)
session.add(item)
session.commit()

item = Item(name = 'Spandex large size swimming cap', description = 'Man, women, large size swimming Waterproof swimming caps, silicone, protect ears', category_id = 1, user_id = 3)
session.add(item)
session.commit()

# Create User's Favorite Items
favorite = Favorite(user_id = 1, item_id = 6)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 1, item_id = 13)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 2, item_id = 3)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 2, item_id = 7)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 3, item_id = 10)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 3, item_id = 12)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 4, item_id = 5)
session.add(favorite)
session.commit()

favorite = Favorite(user_id = 4, item_id = 9)
session.add(favorite)
session.commit()

print ('Mock data created!')