from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Khởi tạo SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Cấu hình ứng dụng
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/school_management'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Khởi tạo cơ sở dữ liệu với ứng dụng
    db.init_app(app)

    # Đăng ký Blueprint
    from .routes import routes
    app.register_blueprint(routes)

    return app
