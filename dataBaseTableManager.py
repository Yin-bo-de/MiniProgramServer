from mysql.connector import Error
import mysql.connector
from loguru import logger

class MySQLConnectionManage:
    def __init__(self, host, user, password):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password  # 在这里输入你的MySQL密码
            )
            if self.connection.is_connected():
                logger.info("连接到 MySQL 数据库成功")
        except Error as e:
            logger.exception(f"连接失败: {e}")

    # 创建数据库
    def create_database(self, databaseName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")  # 创建数据库
            logger.info(f"数据库 {databaseName} 创建成功")
        except Error as e:
            logger.exception(f"创建数据库失败: {e}")

    # 选择数据库
    def use_database(self, databaseName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {databaseName}")  # 使用指定的数据库
            logger.info(f"选择数据库 {databaseName}")
        except Error as e:
            logger.exception(f"选择数据库失败: {e}")

    # 创建表
    def create_table(self, tableName):
        try:
            cursor = self.connection.cursor()
            # 创建一个简单的表
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
                senderName VARCHAR(100) NOT NULL,
                receiverName VARCHAR(100) NOT NULL, 
                Message VARCHAR(100) NOT NULL, 
                RegistrationDate DATETIME
            )
            """)
            logger.info(f"表 {tableName} 创建成功")
        except Error as e:
            logger.exception(f"创建表失败: {e}")

    # 插入数据
    def insert_data(self):
        try:
            cursor = self.connection.cursor()
            # 插入一条数据
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ('Alice', 'alice@example.com'))
            self.connection.commit()  # 提交事务
            logger.info("数据插入成功")
        except Error as e:
            logger.exception(f"插入数据失败: {e}")

    # 查询数据
    def query_data(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users")  # 查询所有数据
            result = cursor.fetchall()  # 获取所有结果
            logger.info("查询结果：")
            for row in result:
                logger.info(row)
        except Error as e:
            logger.exception(f"查询数据失败: {e}")



def initDataBaseTable(databaseName, tableName):
    connectionManage = MySQLConnectionManage(host='localhost', user='root', password='du4ySaAxZu&.')
    if not connectionManage.connection:
        logger.exception("initDataBaseTable fail.")
    connectionManage.create_database(databaseName=databaseName)
    connectionManage.use_database(databaseName=databaseName)
    connectionManage.create_table(tableName=tableName)
    return connectionManage

if __name__ == "__main__":
    initDataBaseTable()

