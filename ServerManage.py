


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
            logger.info(jsonify(message="success", status_code=0))
            return jsonify(message="success", status_code=0)

        """
        用户点击头像进行注册的接口，更新IsRegistered、gender、avatarUrl
        :param name: 
        :return: 
        """
        @self.app.route('/userRegister', methods=['POST'])
        def userRegister():
            data = request.get_json()
            logger.info(f"received userRegister request, data is {data}")
            keyValue = ""
            openid = data['openid']
            if openid != "":
                keyValue += f"openid=\"{openid}\","
            sessionKey = data['sessionKey']
            if sessionKey != "":
                keyValue += f"sessionKey=\"{sessionKey}\","
            avatarUrl = data['avatarUrl']
            if avatarUrl != "":
                keyValue += f"avatarUrl=\"{avatarUrl}\","
            gender = data['gender']
            if gender != "":
                keyValue += f"gender={gender},"
            keyValue += f"IsRegistered=True"
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"")
            if result.__len__() == 0:
                # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey, AvatarUrl, LoverAvatarUrl, Gender)
                self.mySQLConnectionManage.insert_data(tableName=userInfoTableName,
                                                       data=("", openid, "", True, False, "", "", "", "", "", ""))
                logger.info(jsonify(message="success", status_code=200))
                return jsonify(message="success", status_code=200)

            self.mySQLConnectionManage.update_data(tableName=userInfoTableName,
                                                   openid=openid,
                                                   keyValue=keyValue)
            logger.info(jsonify(message="success", status_code=200))
            return jsonify(message="success", status_code=200)

        """
        登陆小程序界面时，请求当前用户的注册状态，并获取对应的头像url展示
        :param name: 
        :return: 
        """
        @self.app.route('/getUserRigisterStatus', methods=['POST'])
        def getUserRigisterStatus():
            data = request.get_json()
            logger.info(f"received getUserRigisterStatus request, data is {data}")
            openid = data['openid']
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName,
                                                           condition=f"WHERE Openid=\"{openid}\"",
                                                           metricsNames="IsRegistered,NickName,AvatarUrl,isHasLover,LoverNickName,LoverAvatarUrl")
            if result.__len__() == 0:
                return jsonify(message="fail",
                               status_code=-1)
            logger.info(result)
            # if result[0][0] == 1:
            #     return jsonify(IsRegistered=result[0][0],
            #                    AvatarUrl=result[0][2],
            #                    NickName=result[0][1],
            #                    isHasLover=result[0][3],
            #                    LoverNickName=result[0][4],
            #                    LoverAvatarUrl=result[0][5],
            #                    message="success",
            #                    status_code=200)
            logger.info(jsonify(IsRegistered=result[0][0],
                           AvatarUrl=result[0][2],
                           NickName=result[0][1],
                           isHasLover=result[0][3],
                           LoverNickName=result[0][4],
                           LoverAvatarUrl=result[0][5],
                           message="success",
                           status_code=200))
            return jsonify(IsRegistered=result[0][0],
                           AvatarUrl=result[0][2],
                           NickName=result[0][1],
                           isHasLover=result[0][3],
                           LoverNickName=result[0][4],
                           LoverAvatarUrl=result[0][5],
                           message="success",
                           status_code=200)

        """
        邀请恋人加入，将恋人的数据更新到自己的数据表，并更新恋人数据表
        :param name: 
        :return: 
        """
        # todo
        @self.app.route('/loverInvite', methods=['POST'])
        def loverInvite():
            data = request.get_json()
            logger.info(f"receive loverInvite request: data: {data}")

            return jsonify(message="success",
                           status_code=200)

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
                    # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey, AvatarUrl, LoverAvatarUrl, Gender)
                    self.mySQLConnectionManage.insert_data(tableName=userInfoTableName, data=("", openid, "", False, False, "", "", "", "", "", ""))
                return jsonify(openid=openid, sessionKey=sessionKey, message="success", status_code=200)
            else:
                return jsonify(message="fail", status_code=401)


    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.app.run(ssl_context=( 'sslFiles/fullchain.pem', 'sslFiles/privkey.pem'), host=self.host, port=self.port)

