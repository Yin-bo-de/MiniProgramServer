


"""
功能描述：lover server manage类
参数：host，监听域名，port监听端口
"""
import json

import requests
from flask import jsonify, request, Flask
from loguru import logger

from dataBaseTableManager import userInfoTableName, commentTableName


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
            nickName = request.args.get('name')
            openid = request.args.get('openid')
            logger.info(f"received get request, name is {nickName}, openid is {openid}")
            # 调用mysql接口查询数据，todo：并将结果按时间排序
            results = self.mySQLConnectionManage.query_data(tableName=commentTableName, condition=f"WHERE \"Openid\"=\"{openid}\" OR receiverOpenid={openid}")
            res_data = {}
            for result in results:
                res_data[result[5]] = {}
                data = {
                    "senderNickName": result[0],
                    "Openid": result[1],
                    "receiverNickName": result[2],
                    "receiverOpenid": result[3],
                    "Message": result[4],
                    "status_code": 0}
                res_data["data"] = data
            return jsonify(res_data)

        """
        监听小程序的发表留言记录的接口
        """
        @self.app.route('/postComment', methods=['POST'])
        def postComment():
            data = request.get_json()
            logger.info(f"received postComment request, data is {data}")
            senderNickName = data['senderNickName']
            Openid = data['Openid']
            receiverNickName = data['receiverNickName']
            receiverOpenid = data['receiverOpenid']
            Message = data['Message']
            # 调用mysql接口插入数据 ("senderNickName", "Openid", "receiverNickName", "receiverOpenid", "Message")
            ret = self.mySQLConnectionManage.insert_data(tableName=commentTableName, data=(senderNickName, Openid, receiverNickName, receiverOpenid, Message))
            if ret != 0:
                logger.error(f"insert data error, data is: {data}")
                return jsonify(message="fail", status_code=-1)
            # 发送响应,jsonify返回json格式的response
            return jsonify(message="success", status_code=0)

        @self.app.route('/userRegister', methods=['POST'])
        def userRegister():
            data = request.get_json()
            logger.info(f"received userRegister request, data is {data}")

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
                result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"")
                if result.__len__() == 0:
                    # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey)
                    self.mySQLConnectionManage.insert_data(tableName=userInfoTableName, data=("", openid, "", False, False, "", "", ""))
                return jsonify(openid=openid, sessionKey=sessionKey, message="success", status_code=200)
            else:
                return jsonify(message="fail", status_code=401)





    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(ssl_context=('example.crt', 'example.key'), host=self.host, port=self.port)

