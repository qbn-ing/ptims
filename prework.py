import os
import time
import docker
import mysql.connector

# 定义MySQL容器的名称和端口号
container_name = "mysql_db"
port = 3306

# 创建Docker客户端
client = docker.from_env()

# 检查MySQL容器是否已经存在
try:
    container = client.containers.get(container_name)
    print("MySQL 容器已经存在.")
except docker.errors.NotFound:
    # 如果MySQL容器不存在，就创建一个新的容器
    print("正在创建 MySQL 容器...")
    container = client.containers.run(
        "mysql:latest",
        detach=True,
        name=container_name,
        environment={
            "MYSQL_ROOT_PASSWORD": "toortoor",
            "MYSQL_DATABASE": "test1"
        },
        ports={f"{port}/tcp": port}
    )
    print("MySQL 容器已创建.")

# 等待MySQL容器启动
print("正在等待 for MySQL容器启动...")
time.sleep(10)

# 连接MySQL数据库
print("连接 MySQL 数据库中...")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toortoor",
    port=port,
    database="test1"
)
mycursor = mydb.cursor()

# 创建数据表
print("创建用户表中...")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS 用户 (编号 INT AUTO_INCREMENT PRIMARY KEY, 用户名 VARCHAR(255), 密码 VARCHAR(255), 邮箱 VARCHAR(255), 状态 ENUM('正常', '停用')DEFAULT '正常')")
print("创建车场表中...")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS 车场 (编号 INT AUTO_INCREMENT PRIMARY KEY, 名称 VARCHAR(255), 地址 VARCHAR(255), 状态 ENUM('正常', '停用')DEFAULT '正常')")
print("创建公交线路表中...")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS 线路 (编号 INT AUTO_INCREMENT PRIMARY KEY, 名称 VARCHAR(255), 所属车场号 INT, 状态 ENUM('正常', '停用','草稿')DEFAULT '正常',包含站点编号 VARCHAR(255),上下行 ENUM('上行','下行')DEFAULT '上行')")
print("创建公交站点表中...")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS 站点 (编号 INT AUTO_INCREMENT PRIMARY KEY, 名称 VARCHAR(255), 经度 FLOAT, 纬度 FLOAT,状态 ENUM('正常', '停用')DEFAULT '正常')")
print("MySQL数据库初始化成功!")
