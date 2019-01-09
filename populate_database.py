#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itemCatalogDatabase_setup import User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Session = sessionmaker(bind=engine)

session = Session()

# Create first user.
user = User(username = 'Admin', email = 'admin@itemcatalog.com')
session.add(user)
session.commit()


# Create item categories.
category = Category(name = 'Consumer Electronics')
session.add(category)
session.commit()

category = Category(name = 'Toys, Kids, Baby')
session.add(category)
session.commit()

category = Category(name = 'Jewelry and Watches')
session.add(category)
session.commit()

category = Category(name = 'Sports and Outdoors')
session.add(category)
session.commit()

# Create items for each category.
# Category 1 - Consumer Electronics
item = Item(name = 'GTF 18650 Rechargeable Battery', description = '3.7V 18650 9800mAh Capacity Li-ion', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'VOGROUND Wireless Controller', description = 'Sony PS4 Dual Shock Vibration Joystick. Bluetooth Wireless Controller', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Cewaal i7s TWS Bluetooth Earphone', description = 'Stereo Earbud Wireless Headphones With Charging Box Mic For xiaomi All Phone', category_id = 1, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Nikon D3400 DSLR Camera', description = '24.2MP - Video - Bluetooth', category_id = 1, user_id = 1)
session.add(item)
session.commit()

# Category 2 - Toys, Kids, Baby
item = Item(name = 'SYMA S8 RC Helicopter', description = 'Remote Control Helicopter Aircraft With Shatter Resistant Light Alloy And Flashing Lights', category_id = 2, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'REAKIDS Beanies Baby Hat', description = 'Cute Pompon Winter Children Knitted Hat', category_id = 2, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Muti-fuction Baby/Adult Digital Termometer', description = 'Infrared Forehead and Body Thermometer No-contact Gun', category_id = 2, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Silicone Training Toothbrush', description = 'BPA Free Banana Shape, Toddler Safe', category_id = 2, user_id = 1)
session.add(item)
session.commit()

# Category 3 - Jewelry and Watches
item = Item(name = 'Vintage Steampunk Retro Watch', description = 'Bronze Pocket Watch, Quartz', category_id = 3, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Marvel Avengers Thor\'s Hammer Keychain', description = 'Mjolnir Metal Model Keyring Pendant', category_id = 3, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Nature Lapel Pins', description = 'Cactus, Palm Leaves, Plants, Trees, Enamel Brooches', category_id = 3, user_id = 1)
session.add(item)
session.commit()

# Category 4 - Sports and Outdoors
item = Item(name = 'KastKing Spartacus Plus Baitcasting Fishing Reel', description = 'Dual Brake System Reel, 8KG Maximum Drag 11+1 BBs 6.3:1', category_id = 4, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Outdoor 3-4 persons automatic speed open tent', description = 'Throwing pop-up windproof waterproof beach camping tent with large inner space', category_id = 4, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Silicone Mouthpiece Teeth Protector', description = 'For Boxing, Baseball, Single Side Mouth Guard', category_id = 4, user_id = 1)
session.add(item)
session.commit()

item = Item(name = 'Spandex large size swimming cap', description = 'Man, women, large size swimming Waterproof swimming caps, silicone, protect ears', category_id = 4, user_id = 1)
session.add(item)
session.commit()

print ('Mock data created!')