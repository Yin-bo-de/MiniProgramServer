from mysql.connector import Error
import mysql.connector
from loguru import logger

from loverServer import userInfoTableName, commentTableName

"""
数据库连接管理类
"""
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

    """
    创建数据库
    tableName：目标库名
    返回值：-1 is fail
    """
    def create_database(self, databaseName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")  # 创建数据库
            logger.info(f"数据库 {databaseName} 创建成功")
            return 0
        except Error as e:
            logger.exception(f"创建数据库失败: {e}")

    """
    选择数据库
    databaseName：目标库名
    返回值：-1 is fail
    """
    def use_database(self, databaseName):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {databaseName}")  # 使用指定的数据库
            logger.info(f"选择数据库 {databaseName}")
            return 0
        except Error as e:
            logger.exception(f"选择数据库失败: {e}")

    """
    创建数据表
    tableName：目标表名
    返回值：-1 is fail
    """
    def create_table(self, tableName):
        try:
            if tableName == userInfoTableName:
                cursor = self.connection.cursor()
                sql = f"""CREATE TABLE IF NOT EXISTS {tableName} (
                    NickName VARCHAR(100) ,
                    Openid VARCHAR(100) NOT NULL PRIMARY KEY, 
                    SessionKey VARCHAR(100), 
                    IsRegistered BOOLEAN DEFAULT FALSE，
                    isHasLover BOOLEAN DEFAULT FALSE,
                    LoverNickName VARCHAR(100) ,
                    loverOpenid VARCHAR(100) UNIQUE,
                    loverSessionKey VARCHAR(100) ,
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                logger.info(f"表 {tableName} 创建成功")
            elif tableName == commentTableName:
                cursor = self.connection.cursor()
                sql = f"""CREATE TABLE IF NOT EXISTS {tableName} (
                    senderNickName VARCHAR(100) NOT NULL,
                    Openid VARCHAR(100) NOT NULL PRIMARY KEY,
                    receiverNickName VARCHAR(100) NOT NULL, 
                    receiverOpenid VARCHAR(100) NOT NULL UNIQUE,
                    Message VARCHAR(100) NOT NULL, 
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                # 创建一个简单的表
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                logger.info(f"表 {tableName} 创建成功")
            return 0
        except Error as e:
            logger.exception(f"创建表失败: {e}")

    """
    向数据表中插入一条数据
    tableName：目标表名
    data：插入数据，格式为tuple: (value1, value2, value3,...)
    返回值：-1 is fail
    """
    def insert_data(self, tableName, data):
        try:
            if tableName == userInfoTableName:
                cursor = self.connection.cursor()
                sql = f"""INSERT INTO {tableName} "
                    (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey) 
                    VALUES (%s, %s，%s, %s，%s, %s %s, %s)"""
                # 插入一条数据
                cursor.execute(
                    operation=sql,
                    params=data)
                logger.info(f"insert data sql: {sql} {data}")
                self.connection.commit()  # 提交事务
                logger.info("数据插入成功")
            elif tableName == commentTableName:
                cursor = self.connection.cursor()
                sql = f"""INSERT INTO {tableName} 
                    (senderNickName, Openid, receiverNickName, receiverOpenid, Message) 
                    VALUES (%s, %s, %s, %s, %s)"""
                logger.info(f"insert data sql: {sql} {data}")
                # 插入一条数据
                cursor.execute(
                    operation=sql,
                    params=data)
                self.connection.commit()  # 提交事务
                logger.info("数据插入成功")
            return 0
        except Error as e:
            logger.exception(f"插入数据失败: {e}")


    """
    查询数据
    tableName:查询表名
    condition:查询数据的过滤条件，list格式，["key1=value1", "key2<value2", "key3>value3"]
    返回值：-1 is fail
    """
    def query_data(self, tableName, condition:list):
        try:
            if condition.__len__() == 0:
                return -1
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM {tableName}"
            if condition.__len__() > 0:
                sql += " WHERE "
                for item in condition:
                    if item is condition[-1]:
                        sql += item
                        break
                    sql += item + " AND "
            logger.info(f"query data sql: {sql}")
            cursor.execute(operation=sql)
            result = cursor.fetchall()  # 获取所有结果
            logger.info(f"查询结果size：{result.__len__()}")
            # for row in result:
            #     logger.info(row)
            return result
        except Error as e:
            logger.exception(f"查询数据失败: {e}")

    """
    更新数据
    tableName:表名
    openid:对应数据的过滤条件
    keyValue:需要修改的目标colName和colValue，list格式，["key1=value1", "key2=value2", "key3=value3"]
    返回值：0 is success, -1 is fail
    """
    def update_data(self, tableName:str, openid:str, keyValue:list):
        try:
            if keyValue.__len__() == 0:
                logger.error("keyValue is empty.")
                return -1
            cursor = self.connection.cursor()
            sql = f"UPDATE {tableName} SET"
            for item in keyValue:
                if item is keyValue[-1]:
                    sql += item
                    break
                sql += item + ", "
            sql += f" WHERE Openid = {openid}"
            cursor.execute(operation=sql)
            return 0
        except Error as e:
            logger.exception(f"更新数据失败: {e}")


"""
功能描述：初始化mysql数据库和对应的表
databaseName:库名
tableName:表名
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

