import os

from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
import stripe

root_path = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    "__name__",
    template_folder=os.path.join(root_path, 'templates'),   # nơi chứa .html
    static_folder=os.path.join(root_path, 'static')         # nơi chứa static (css, js, ảnh)
)
app.secret_key = "Us8k2s2@#*$jjudj^8&**tgfsgYFS677*&6s8suuuu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstorev2?charset=utf8mb4" % quote('123456')
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login_manager = LoginManager(app)

# Configuration cloudinary
cloudinary.config(
    cloud_name = "drzc4fmxb",
    api_key = "422829951512966",
    api_secret = "ILJ11vG7Q7OqbjxyhWS1lNJMN5U", # Click 'View API Keys' above to copy your API secret
    secure=True
)

stripe.api_key = ''

