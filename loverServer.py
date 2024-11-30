import json
import ssl
from aifc import Error

from loguru import logger
from dataBaseTableManager import initDataBaseTable
from commentRecord.readComment import ReadComment
from flask import Flask, request, jsonify, Response

databaseName = "loverDatabase"
tableName = "loverCommentTable" # 留言记录数据表，保存：【日期】【发送方name】【接收方name】【Message】
connectionManage = initDataBaseTable(databaseName, tableName)

def initLog():
    logger.add("log/app.log", rotation="00:00:00")  # 每天午夜自动生成新日志文件


class ServerManage():
    def __init__(self, host='127.0.0.1', port=8081):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        # https://0.0.0.0:8081/comment?name="yinbo"
        @self.app.route('/getComment', methods=['GET'])
        def getComment():
            name = request.args.get('name')
            logger.info(f"received get request, name is {name}")
            # 调用mysql接口查询数据

            return jsonify(message="success", status="success")


        @self.app.route('/postComment', methods=['POST'])
        def postComment():
            data = request.get_json()
            logger.info(f"received post request, data is {data}")
            # 调用mysql接口插入数据

            # 发送响应,jsonify返回json格式的response
            return jsonify(message="success", status="success")

    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(ssl_context=('example.crt', 'example.key'), host=self.host, port=self.port)

if __name__ == "__main__":
    initLog()
    serverManage = ServerManage(host="0.0.0.0", port=8081)
    serverManage.run()
