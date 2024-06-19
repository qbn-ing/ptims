from datetime import timedelta
from app.main.routes import bp
from flask import Flask
from app.db import mysql
import csv

def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'toortoor'
    app.config['MYSQL_mysql'] = 'test1'
    app.config['MYSQL_DB'] = 'test1'
    app.secret_key = 'testmysql112'  # os.urandom(32)
    mysql.init_app(app)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 生成过期日期
    from .main.routes import bp
    app.register_blueprint(bp)

    return app