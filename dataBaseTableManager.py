from cgi import logfp

from mysql.connector import Error
import mysql.connector
from loguru import logger

databaseName = "loverDatabase"
commentTableName = "CommentTable" # 留言记录数据表，保存：【日期】【发送方name】【接收方name】【Message】
userInfoTableName = "userInfoTable" # 记录每个用户的openid，用于判断用户是否注册状态【nickName】【openid】【sessionKey】【】
# connectionManage = initDataBaseTable(databaseName, commentTableName)



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
                    IsRegistered BOOLEAN DEFAULT FALSE,
                    isHasLover BOOLEAN DEFAULT FALSE,
                    LoverNickName VARCHAR(100) ,
                    loverOpenid VARCHAR(100) UNIQUE,
                    loverSessionKey VARCHAR(100) ,
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                self.connection.commit()
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
                self.connection.commit()
                logger.info(f"表 {tableName} 创建成功")
            return 0
        except Error as e:
            logger.exception(f"创建表失败: {e}")

    """
    删除数据表
    tableName：目标表名
    返回值：-1 is fail
    """
    def drop_table(self, tableName:str):
        try:
            cursor = self.connection.cursor()
            sql = f"DROP TABLE IF EXISTS {tableName}"
            logger.info(f"drop table sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"创建表失败: {e}")

    """
    查询数据表
    返回值：-1 is fail，成功返回tables（元组List，表名在第一个元素）
    """
    def query_table(self):
        try:
            cursor = self.connection.cursor()
            sql = f"SHOW TABLES"
            logger.info(f"query table sql: {sql}")
            cursor.execute(operation=sql)
            tables = cursor.fetchall()
            logger.info("当前数据库中的表有：")
            for table in tables:
                logger.info(table[0])
            return tables
        except Error as e:
            logger.exception(f"查询表失败: {e}")

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
                sql = f"""INSERT INTO {tableName}
                    (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                logger.info(f"insert data sql: {sql} {data}")
                # 插入一条数据
                cursor.execute(
                    operation=sql,
                    params=data)
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
    condition:查询数据的过滤条件，str格式，"WHERE key1=value1 AND key2<value2 OR key3>value3"
    返回值：-1 is fail
    """
    def query_data(self, tableName, condition:str):
        try:
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM {tableName} {condition}"
            # if condition.__len__() > 0:
            #     sql += " WHERE "
            #     for item in condition:
            #         if item is condition[-1]:
            #             sql += item
            #             break
            #         sql += item + " AND "
            logger.info(f"query data sql: {sql}")
            cursor.execute(operation=sql)
            result = cursor.fetchall()  # 获取所有结果
            logger.info(f"查询结果size：{result.__len__()}")
            for row in result:
                logger.info(row)
            return result
        except Error as e:
            logger.exception(f"查询数据失败: {e}")

    """
    更新数据
    tableName:表名
    openid:对应数据的过滤条件
    keyValue:需要修改的目标colName和colValue，str，"key1=value1, key2=value2, key3=value3"
    返回值：0 is success, -1 is fail
    """
    def update_data(self, tableName:str, openid:str, keyValue:str):
        try:
            if keyValue.__len__() == 0:
                logger.error("keyValue is empty.")
                return -1
            cursor = self.connection.cursor()
            sql = f"UPDATE {tableName} SET {keyValue}"
            # for item in keyValue:
            #     if item is keyValue[-1]:
            #         sql += item
            #         break
            #     sql += item + ", "
            sql += f" WHERE Openid = {openid}"
            logger.info(f"update sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"更新数据失败: {e}")

    """
    删除数据
    tableName:表名
    openid:对应数据的过滤条件，删除这一行
    返回值 -1 is fail
    """
    def del_data(self, tableName:str, openid:str):
        try:
            cursor = self.connection.cursor()
            sql = f"DELETE FROM {tableName} WHERE Openid={openid}"
            logger.info(f"del_data sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"删除数据失败: {e}")


