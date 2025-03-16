import json
import ssl
import requests
from loguru import logger

from ServerManage import ServerManage
from dataBaseTableManager import MySQLConnectionManage, databaseName, commentTableName, userInfoTableName

MacroEnvDebug = True  # 定义数据库连接环境，True表示本地远程连接调试，False表示本地连接


def initLog():
    logger.add("log/app.log", rotation="00:00:00")  # 每天午夜自动生成新日志文件

def initDataBaseTable(databaseName, tableNameList:list):
    """
    功能描述: 初始化mysql数据库和对应的表
    databaseName:库名
    tableName:表名,list格式，多个表名同时传入: ["tableName1", "tableName2", ...]
    返回值: 数据库操作handler
    """
    if MacroEnvDebug:
        connectionManage = MySQLConnectionManage(host='47.122.28.9', user='yinbo_debug', password='du4ySaAxZu&.')
    else:
        connectionManage = MySQLConnectionManage(host='localhost', user='root', password='du4ySaAxZu&.')
    if not connectionManage.connection:
        logger.exception("initDataBaseTable fail.")
    connectionManage.create_database(databaseName=databaseName)
    connectionManage.use_database(databaseName=databaseName)
    for tableName in tableNameList:
        connectionManage.create_table(tableName=tableName)
    return connectionManage

if __name__ == "__main__":
    initLog()
    mySQLConnectionManage = initDataBaseTable(databaseName=databaseName, tableNameList=[userInfoTableName, commentTableName])
    serverManage = ServerManage(mySQLConnectionManage=mySQLConnectionManage, host="0.0.0.0", port=8081)
    serverManage.run()
