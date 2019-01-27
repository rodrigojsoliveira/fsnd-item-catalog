# Item Catalog
Browse an item catalog and view the products available in each category. Login to add, edit and delete items.

This project is part os Udacity´s Full Stack Web Developer Nanodegree. File `fsnd-virtual-machine.zip` was created by the Udacity team specifically for this Nanodegree.

## Virtual Machine Setup
In order to run the code, you will need to install some software. They are:

1. **VirtualBox**. This is virtualization software that will let you run a virtual machine on your computer. Visit https://www.virtualbox.org/, download the package for your system and install it.
1. **Vagrant**. Vagrant is a tool for building and managing virtual machine environments. Download it at https://www.vagrantup.com/.

After installing both softwares you will use the virtual machine configuration file inside `fsnd-virtual-machine.zip`. Unzip the archive to a new directory, change into it and you should find a folder called **vagrant**.

Change into the **vagrant** folder and type `vagrant up`. This will set up a Linux environment. This step may take a few minutes.

When you see your shell prompt again, type `vagrant ssh` and you will log into your new Linux virtual machine. You should see a shell prompt starting with the word `vagrant`.

Change to folder `/vagrant`. This folder is shared between your computer and the virtual machine, so you should be able to edit code and run it on your VM.

## Configuring the Item Catalog Database
Clone this repo to folder `/vagrant/catalog`. This folder will by synched to `/vagrant/catalog` within the virtual machine.

Run file `itemCatalogDatabase_setup.py` to create the database.

Populate the database with initial data by running file `populate_database.py`.

## Running the Application
To start the server, run `catalog.py` inside your `vagrant` folder. In your browser, go to `http://localhost:5000`. The item catalog should be displayed.

## API Endpoints
There are a few endpoints you can go to retrieve JSON information from the catalog. They are:
1. `/json/categories/` - Lists all categories in the catalog.
1. `/json/items/` - Lists all items in the catalog.
1. `/json/<string:category>/items/` - Lists all items in a specified catalog.
1. `/json/<string:category>/items/<int:item_id>/` - Lists a specific item from a given category.


## Python version
You will need Python 3 installed on your system to run the log analysis tool.




