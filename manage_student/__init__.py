from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = 'KJHJF^(&*&&*OHH&*%&*TYUGJHG&(T&IUHKB'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/student_management?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
db = SQLAlchemy(app=app)
migrate = Migrate(app, db)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name="dxxwcby8l",
    api_key="448651448423589",
    api_secret="ftGud0r1TTqp0CGp5tjwNmkAm-A",
    secure=True
)