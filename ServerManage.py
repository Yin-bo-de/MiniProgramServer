


"""
功能描述：lover server manage类
参数：host，监听域名，port监听端口
"""
import json

import requests
from flask import jsonify, request, Flask
from loguru import logger

from dataBaseTableManager import userInfoTableName


class ServerManage():
    def __init__(self, mySQLConnectionManage, host='127.0.0.1', port=8081):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.mySQLConnectionManage = mySQLConnectionManage

        """
        监听小程序的获取留言记录的接口
        """
        @self.app.route('/getComment', methods=['GET'])
        def getComment():
            name = request.args.get('name')
            logger.info(f"received get request, name is {name}")
            # 调用mysql接口查询数据

            return jsonify(message="success", status="success")

        """
        监听小程序的发表留言记录的接口
        """
        @self.app.route('/postComment', methods=['POST'])
        def postComment():
            data = request.get_json()
            logger.info(f"received post request, data is {data}")
            # 调用mysql接口插入数据

            # 发送响应,jsonify返回json格式的response
            return jsonify(message="success", status="success")

        """
        获取用户的唯一标识openid和对应的seesionkey
        :param name: 
        :return: 
        """
        @self.app.route('/getOpenid', methods=['POST'])
        def getOpenid():
            data = request.get_json()
            code = data['code']
            appid = "wx282724f41dc342b5"
            secret = "006218817bcce2df7fc175adeb4e5743"
            logger.info(f"getOpenid() request: {data}")
            url = "https://api.weixin.qq.com/sns/jscode2session" # 用于请求wx 获取openid的接口
            responses = requests.get(
                url=url,
                params={
                    "appid": appid,
                    "secret": secret,
                    "js_code": code,
                    "grant_type": 'authorization_code'
                }
            )
            logger.info(f"request https://api.weixin.qq.com/sns/jscode2session, response is: {responses}")
            if responses.status_code == 200:
                res_json = json.loads(responses.text)
                openid = res_json['openid']
                sessionKey = res_json['session_key']
                # todo 判断当前数据是否已经存在，来决策时更新还是插入新的数据。将openid和sessionKey写入表userInfoTableName中
                result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=[f"\"Openid\"=\"{openid}\""])
                if result.__len__() == 0:
                    # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey)
                    self.mySQLConnectionManage.insert_data(tableName=userInfoTableName, data=("", openid, "", False, False, "", "", ""))
                return jsonify(openid=openid, sessionKey=sessionKey, status="success", status_code=200)
            else:
                return jsonify(status="fail", status_code=401)


        @self.app.route('/userRegister', methods=['POST'])
        def userRegister():
            data = request.get_json()





    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(ssl_context=('example.crt', 'example.key'), host=self.host, port=self.port)

