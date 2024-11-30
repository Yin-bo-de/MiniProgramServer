from mysql.connector import Error
import mysql.connector
from loguru import logger

from loverServer import userInfoTableName, commentTableName


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
            if tableName == userInfoTableName:
                cursor = self.connection.cursor()
                cursor.execute(f"""
                                CREATE TABLE IF NOT EXISTS {tableName} (
                                    NickName VARCHAR(100) ,
                                    Openid VARCHAR(100) NOT NULL PRIMARY KEY, 
                                    SessionKey VARCHAR(100), 
                                    IsRegistered BOOLEAN DEFAULT FALSE，
                                    isHasLover BOOLEAN DEFAULT FALSE,
                                    LoverNickName VARCHAR(100) ,
                                    loverOpenid VARCHAR(100) UNIQUE,
                                    loverSessionKey VARCHAR(100) ,
                                    RegistrationDate DATETIME
                                )
                                """)
                logger.info(f"表 {tableName} 创建成功")
            elif tableName == commentTableName:
                cursor = self.connection.cursor()
                # 创建一个简单的表
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {tableName} (
                    senderNickName VARCHAR(100) NOT NULL,
                    senderOpenid VARCHAR(100) NOT NULL UNIQUE,
                    receiverNickName VARCHAR(100) NOT NULL, 
                    receiverOpenid VARCHAR(100) NOT NULL UNIQUE,
                    Message VARCHAR(100) NOT NULL, 
                    RegistrationDate DATETIME
                )
                """)
                logger.info(f"表 {tableName} 创建成功")
        except Error as e:
            logger.exception(f"创建表失败: {e}")

    # 插入数据
    def insert_data(self, tableName):
        try:
            if tableName == userInfoTableName:
                cursor = self.connection.cursor()
                # 插入一条数据
                cursor.execute(
                    f"INSERT INTO {tableName} (name, email) VALUES (%s, %s)",
                    ('Alice', 'alice@example.com'))
                self.connection.commit()  # 提交事务
                logger.info("数据插入成功")
            elif tableName == commentTableName:
                cursor = self.connection.cursor()
                # 插入一条数据
                cursor.execute(
                    f"INSERT INTO {tableName} (name, email) VALUES (%s, %s)",
                    ('Alice', 'alice@example.com'))
                self.connection.commit()  # 提交事务
                logger.info("数据插入成功")
        except Error as e:
            logger.exception(f"插入数据失败: {e}")

    # 查询数据
    def query_data(self, tableName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * "
                f"FROM {tableName} "
                f"WHERE key=value")  # 查询所有数据
            result = cursor.fetchall()  # 获取所有结果
            logger.info("查询结果：")
            for row in result:
                logger.info(row)
        except Error as e:
            logger.exception(f"查询数据失败: {e}")

    def update_data(self, tableName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
            UPDATE {tableName}
            SET name = %s, email = %s
            WHERE id = %s
            """)
        except Error as e:
            logger.exception(f"更新数据失败: {e}")


"""
功能描述：初始化mysql数据库和对应的表
参数：databaseName库名， tableName表名
返回值：数据库操作handler
"""
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

