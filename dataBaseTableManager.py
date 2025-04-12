from mysql.connector import Error
import mysql.connector
from loguru import logger

databaseName = "loverDatabase"
commentTableName = "CommentTable" # 留言记录数据表, 保存: 【日期】【发送方name】【接收方name】【Message】
userInfoTableName = "userInfoTable" # 记录每个用户的openid, 用于判断用户是否注册状态【nickName】【openid】【sessionKey】【】
ImageTable = "ImageTable"
# connectionManage = initDataBaseTable(databaseName, commentTableName)




class MySQLConnectionManage:
    """
    数据库连接管理类
    """
    def __init__(self, host, user, password):
        """初始化数据库连接"""
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
            self.connection = None


    def create_database(self, databaseName):
        """创建数据库
        tableName: 目标库名
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")  # 创建数据库
            logger.info(f"数据库 {databaseName} 创建成功")
            return 0
        except Error as e:
            logger.exception(f"创建数据库失败: {e}")
            return -1
        finally:
            cursor.close()

    def use_database(self, databaseName):
        """选择数据库
        databaseName: 目标库名
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {databaseName}")  # 使用指定的数据库
            logger.info(f"选择数据库 {databaseName}")
            return 0
        except Error as e:
            logger.exception(f"选择数据库失败: {e}")
            return -1
        finally:
            cursor.close()
 
    def create_table(self, tableName):
        """创建数据表
        tableName: 目标表名
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            if tableName == userInfoTableName:
                sql = f"""CREATE TABLE IF NOT EXISTS {tableName} (
                    NickName VARCHAR(100) ,
                    Openid VARCHAR(100) NOT NULL PRIMARY KEY, 
                    SessionKey VARCHAR(100), 
                    IsRegistered BOOLEAN DEFAULT FALSE,
                    isHasLover BOOLEAN DEFAULT FALSE,
                    LoverNickName VARCHAR(100) ,
                    loverOpenid VARCHAR(100) UNIQUE,
                    loverSessionKey VARCHAR(100) ,
                    AvatarUrl VARCHAR(1000),
                    LoverAvatarUrl VARCHAR(1000),
                    Gender VARCHAR(1000),
                    LoverGender VARCHAR(1000),
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                self.connection.commit()
                logger.info(f"表 {tableName} 创建成功")
            elif tableName == commentTableName:
                cursor = self.connection.cursor()
                sql = f"""CREATE TABLE IF NOT EXISTS {tableName} (
                    senderNickName VARCHAR(100),
                    Openid VARCHAR(100) NOT NULL,
                    receiverNickName VARCHAR(100), 
                    receiverOpenid VARCHAR(100) NOT NULL,
                    Message VARCHAR(100) NOT NULL, 
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                # 创建一个简单的表
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                self.connection.commit()
                logger.info(f"表 {tableName} 创建成功")
            elif tableName == ImageTable:
                cursor = self.connection.cursor()
                sql = f"""CREATE TABLE IF NOT EXISTS {tableName} (
                    uploaderNickName VARCHAR(100),
                    senderOpenid VARCHAR(100) NOT NULL,
                    receiverOpenid VARCHAR(100) NOT NULL, 
                    ImageUrl VARCHAR(1000) NOT NULL,
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP)"""
                # 创建一个简单的表
                logger.info(f"create talbe sql: {sql}")
                cursor.execute(operation=sql)
                self.connection.commit()
                logger.info(f"表 {tableName} 创建成功")
            return 0
        except Error as e:
            logger.exception(f"创建表失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()

    def drop_table(self, tableName:str):
        """删除数据表
        tableName: 目标表名
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            sql = f"DROP TABLE IF EXISTS {tableName}"
            logger.info(f"drop table sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"创建表失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()

    def query_table(self):
        """查询数据表
        返回值: -1 is fail, 成功返回tables(元组List, 表名在第一个元素)
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            sql = f"SHOW TABLES"
            logger.info(f"query table sql: {sql}")
            cursor.execute(operation=sql)
            tables = cursor.fetchall()
            logger.info("当前数据库中的表有: ")
            for table in tables:
                logger.info(str(table[0])) # type: ignore
            return tables
        except Error as e:
            logger.exception(f"查询表失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()
  
    def insert_data(self, tableName, data):
        """向数据表中插入一条数据
        tableName: 目标表名
        data: 插入数据, 格式为tuple: (value1, value2, value3,...)
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            if tableName == userInfoTableName:
                cursor = self.connection.cursor()
                sql = f"""INSERT INTO {tableName}
                    (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey, AvatarUrl, LoverAvatarUrl, Gender, LoverGender) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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
            elif tableName == ImageTable:
                cursor = self.connection.cursor()
                sql = f"""INSERT INTO {tableName} 
                    (uploaderNickName, senderOpenid, receiverOpenid, ImageUrl)
                    VALUES (%s, %s, %s, %s)"""
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
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()


    def query_data(self, tableName, condition:str, metricsNames=''):
        """查询数据
        tableName:查询表名
        condition:查询数据的过滤条件, str格式, "WHERE key1=value1 AND key2<value2 OR key3>value3"
        metricsName:查询的指标名,默认查询所有指标, str格式, "Nickname,Openid,loverNickName"
        返回值: -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            if metricsNames == '':
                sql = f"SELECT * FROM {tableName} {condition}"
            else:
                sql = f"SELECT {metricsNames} FROM {tableName} {condition}"
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
            logger.info(f"查询结果size: {result.__len__()}")
            for row in result:
                logger.info(row)
            return result
        except Error as e:
            logger.exception(f"查询数据失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()

    def update_data(self, tableName:str, openid:str, keyValue:str):
        """更新数据
        tableName:表名
        openid:对应数据的过滤条件
        keyValue:需要修改的目标colName和colValue, str, "key1=value1, key2=value2, key3=value3"
        返回值: 0 is success, -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
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
            sql += f" WHERE Openid=\"{openid}\""
            logger.info(f"update sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"更新数据失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()


    def del_data(self, tableName:str, openid:str):
        """删除数据
        tableName:表名
        openid:对应数据的过滤条件, 删除这一行
        返回值 -1 is fail
        """
        if self.connection is None:
            logger.error("数据库连接未建立")
            return -1
        try:
            cursor = self.connection.cursor()
            sql = f"DELETE FROM {tableName} WHERE Openid=\"{openid}\""
            logger.info(f"del_data sql: {sql}")
            cursor.execute(operation=sql)
            self.connection.commit()
            return 0
        except Error as e:
            logger.exception(f"删除数据失败: {e}")
            self.connection.rollback()
            return -1

        finally:
            if self.connection.is_connected():
                cursor.close()


if __name__ == "__main__":
    connectionManage = MySQLConnectionManage(host='47.122.28.9', user='yinbo_debug', password='du4ySaAxZu&.')
    # connectionManage.create_database(databaseName=databaseName)
    connectionManage.use_database(databaseName=databaseName)
    connectionManage.drop_table(tableName=ImageTable)
    # connectionManage.del_data(tableName=userInfoTableName, openid='oufmR7QHwb9gH4iRjW1CmkGG5enM')