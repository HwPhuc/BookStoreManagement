# Book Store Project

This is a Flask web application for a book store.

## About The Project
1. **User**
- Login/Register
- Buy books online
- Pre-order books for in-store pickup
- Add books to the shopping cart
- View personal purchase history
2. **Importer**
- Add new books to the system
- View personal book import history
3. **Employee**
- Create new invoices for in-store purchases
- Confirm orders when customers pick up pre-ordered books
 - View personal sales history
4. **Admin**
- Manage users (view, edit, delete User, Importer, Employee accounts)
- View sales and inventory reports

## Prerequisites

- Python 3.x
- Flask 3.x or later
- pip (Python package installer)
- Stripe
- Cloudinary 

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/VanThanh09/salebook
    ```

   ```bash
   cd salebook
   ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
   ```

     - For Windows:
   
       ```bash
       venv\Scripts\activate
       ```

     - For Linux:

        ```bash
        sudo apt-get install -y mysql-server
        ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Database setup:**

    - Install the database MySQL:

        For Windows: Download and install MySQL from [here](https://dev.mysql.com/downloads/installer/).

        For Linux:

        ```bash
        sudo apt-get install -y mysql-server
        ```

    - Login to MySQL:

        In this project we use user `root` with password `123456`, database name: `bookstorev2`, charset: `utf8` and collation: `utf8_unicode_ci`.

        You can configure the database in `salebook/__init__.py` `line 10` using the following syntax:

        ```python
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://<your_database_user>:%s@localhost/<your_database_name>?charset=utf8mb4" % quote('<your_database_password>')
        ```

        Change `<your_database_user>`, `<your_database_name>`, and `<your_database_password>` with your setting.

    - Run the models to create tables: Run file `salebook/models.py`
   
        ```bash
        python -m SaleBook.models
        ```
   
    - If you see : `success to create database` you are done.

   
## Runing project


   - Run file salebook/`index.py`

        ```bash
        python -m SaleBook.index
        ```


## Accout

1. **Admin:** http://`<your-localhost>`/admin

    
  - Username: admin

   
  - Password: 123

   
2. **Inventory Manager:** http://`<your-localhost>`/import_book

   
  - Username: importer

   
  - Password: 123

   
3. **Employee:** http://`<your-localhost>`/sale_book

   
  - Username: employee


  - Password: 123

   
4. **User:**

  - Register new accout
   

