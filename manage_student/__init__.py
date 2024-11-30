from flask import Flask
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)

# Cấu hình ứng dụng
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/school_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
__table_args__ = {'extend_existing': True}
# Khởi tạo cơ sở dữ liệu với ứng dụng
db = SQLAlchemy(app)

# # Đăng ký Blueprint
# from .routes import routes
#
# app.register_blueprint(routes)
