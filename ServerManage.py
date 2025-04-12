"""
功能描述: lover server manage类
参数: host, 监听域名, port监听端口
"""
import datetime
import json
import os
import string
from tkinter import Image

import requests
from flask import jsonify, request, Flask
from loguru import logger
from minio import Minio, S3Error

from Utils import minio_tos
from dataBaseTableManager import *


class ServerManage():
    def __init__(self, mySQLConnectionManage, host='127.0.0.1', port=8081):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.mySQLConnectionManage = mySQLConnectionManage


        @self.app.route('/getComment', methods=['GET'])
        def getComment():
            """
            监听小程序的获取留言记录的接口，这里应该控制一次性返回的条数
            """
            res_data = {}
            nickName = request.args.get('name')
            openid = request.args.get('openid')
            logger.info(f"received get request, name is {nickName}, openid is {openid}")
            # 调用mysql接口查询数据, todo: 并将结果按时间排序
            results = self.mySQLConnectionManage.query_data(tableName=commentTableName, condition=f"WHERE Openid=\"{openid}\" OR receiverOpenid=\"{openid}\"")
            if results.__len__() == 0:
                res_data["code"] = 501
                res_data["message"] = "no data in database"
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            res_data["data"] = []
            for result in results:
                data = {
                    "senderNickName": result[0],
                    "Openid": result[1],
                    "receiverNickName": result[2],
                    "receiverOpenid": result[3],
                    "Message": result[4],
                    "datatime": result[5],
                    "status_code": 0
                }
                res_data["data"].append(data)
            res_data["message"] = "success"
            res_data["status_code"] = 200
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)


        @self.app.route('/postComment', methods=['POST'])
        def postComment():
            """
            监听小程序的发表留言记录的接口
            """
            data = request.get_json()
            logger.info(f"received postComment request, data is {data}")
            res_data = {}
            senderNickName = data.get('senderNickName')
            Openid = data.get('openid')
            receiverNickName = data.get('receiverNickName')
            receiverOpenid = data.get('receiverOpenid')
            Message = data.get('message')
            # 调用mysql接口插入数据 ("senderNickName", "Openid", "receiverNickName", "receiverOpenid", "Message")
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{Openid}\"", metricsNames="IsRegistered")
            if result.__len__() == 0 or (result.__len__() != 0 and result[0][0] == False):
                logger.error(f"insert data error, user is not register.")
                res_data["message"] = "fail, user is not register."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            ret = self.mySQLConnectionManage.insert_data(tableName=commentTableName, data=(senderNickName, Openid, receiverNickName, receiverOpenid, Message))
            if ret != 0:
                logger.error(f"insert data error, data is: {data}")
                res_data["message"] = "fail"
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            res_data["message"] = "success"
            res_data["status_code"] = 0
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)


        @self.app.route('/userRegister', methods=['POST'])
        def userRegister():
            """
            用户点击头像进行注册的接口, 更新IsRegistered、gender、avatarUrl
            :param name:
            :return:
            """
            data = request.get_json()
            logger.info(f"received userRegister request, data is {data}")
            keyValue = []
            openid = data.get('openid')
            if openid:
                keyValue.append(f"openid=\"{openid}\"")
            sessionKey = data.get('sessionKey')
            if sessionKey:
                keyValue.append(f"sessionKey=\"{sessionKey}\"")
            avatarUrl = data.get('avatarUrl')
            if avatarUrl:
                keyValue.append(f"avatarUrl=\"{avatarUrl}\"")
            gender = data.get('gender')
            if gender:
                keyValue.append(f"gender=\"{gender}\"")
            nickName = data.get('nickName')
            if nickName:
                keyValue.append(f"NickName=\"{nickName}\"")
            keyValue.append("IsRegistered=True")
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"")
            res_data = {}
            if result.__len__() == 0:
                # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey, AvatarUrl, LoverAvatarUrl, Gender, LoverGender)
                self.mySQLConnectionManage.insert_data(tableName=userInfoTableName,
                                                       data=(nickName, openid, sessionKey, True, False, "", None, "", avatarUrl, "", gender, "")) # type: ignore
                res_data["message"] = "success"
                res_data["status_code"] = 200
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)

            self.mySQLConnectionManage.update_data(tableName=userInfoTableName,
                                                   openid=openid,
                                                   keyValue=", ".join(keyValue))
            res_data["message"] = "success"
            res_data["status_code"] = 200
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)
        
        @self.app.route('/uploadImage', methods=['POST'])
        def uploadImage():
            """
            用户上传图片
            :param name:
            :return:
            """
            data = request.get_json()
            logger.info(f"received userRegister request, data is {data}")
            openid = data.get('openid')
            sessionKey = data.get('sessionKey')
            imageUrl = data.get('imageUrl')
            uploaderNickName = data.get('uploaderNickName')
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"")
            res_data = {}
            if result.__len__() == 0: 
                res_data["message"] = "fail, user not register."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"", metricsNames="loverOpenid")
            logger.info("result: ", result[0])
            loverOpenid = result[0][0]
            # (uploaderNickName, senderOpenid, receiverOpenid, ImageUrl)
            logger.info("loverOpenid: " + loverOpenid)
            self.mySQLConnectionManage.insert_data(tableName=ImageTable, data=(uploaderNickName, openid, loverOpenid, imageUrl)) # type: ignore
            res_data["message"] = "success"
            res_data["status_code"] = 200
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)

        @self.app.route('/getUserRigisterStatus', methods=['POST'])
        def getUserRigisterStatus():
            """
            登陆小程序界面时, 请求当前用户的注册状态, 并获取对应的头像url展示
            :param name:
            :return:
            """
            data = request.get_json()
            logger.info(f"received getUserRigisterStatus request, data is {data}")
            openid = data.get('openid')
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName,
                                                           condition=f"WHERE Openid=\"{openid}\"",
                                                           metricsNames="IsRegistered,NickName,AvatarUrl,isHasLover,LoverNickName,LoverAvatarUrl")
            result2 = self.mySQLConnectionManage.query_data(tableName=ImageTable,
                                                              condition=f"WHERE senderOpenid=\"{openid}\" OR receiverOpenid=\"{openid}\"",
                                                              metricsNames="ImageUrl")
            imageUrls = []
            for item in result2:
                imageUrls.append(item[0])
            res_data = {}
            if result.__len__() == 0:
                res_data["message"] = "fail"
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            res_data = {
                "IsRegistered": result[0][0],
                "AvatarUrl": result[0][2],
                "NickName": result[0][1],
                "isHasLover": result[0][3],
                "LoverNickName": result[0][4],
                "LoverAvatarUrl": result[0][5],
                "ImageUrls": imageUrls,
                "message": "success",
                "status_code": 200
            }
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)


        # todo
        @self.app.route('/bindLover', methods=['POST'])
        def bindLover():
            """
            将恋人的数据更新到自己的数据表
            :param name:
            :return:
            """
            res_data = {}
            data = request.get_json()
            logger.info(f"receive loverInvite request: data: {data}")
            openid = data.get('openid')
            loverOpenid = data.get('loverOpenid')
            keyValue = []
            if loverOpenid:
                keyValue.append(f"loverOpenid=\"{loverOpenid}\"")
            else:
                logger.error(f"lover openid error.")
                res_data["message"] = "fail, lover openid error."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            keyValue.append("isHasLover=True")
            # 受邀请方
            result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{loverOpenid}\"", metricsNames="IsRegistered,AvatarUrl,SessionKey,Gender,NickName")
            if result.__len__() == 0 or (result.__len__() != 0 and result[0][0] == False):
                logger.error(f"insert data error, lover is not register.")
                res_data["message"] = "fail, lover is not register."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            keyValue.append(f"LoverAvatarUrl=\"{result[0][1]}\"")
            keyValue.append(f"loverSessionKey=\"{result[0][2]}\"")
            keyValue.append(f"loverGender=\"{result[0][3]}\"")
            keyValue.append(f"loverNickName=\"{result[0][4]}\"")
            res_data['LoverAvatarUrl'] = result[0][1]
            ret = self.mySQLConnectionManage.update_data(tableName=userInfoTableName, openid=openid, keyValue=", ".join(keyValue))
            if ret == -1:
                res_data["message"] = "update date fail."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)

            # 邀请方
            keyValue2 = []
            keyValue2.append(f"loverOpenid=\"{openid}\"")
            result2 = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"", metricsNames="IsRegistered,AvatarUrl,SessionKey,Gender,NickName")
            if result2.__len__() == 0 or (result2.__len__() != 0 and result2[0][0] == False):
                logger.error(f"insert data error, lover is not register.")
                res_data["message"] = "fail, lover is not register."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            keyValue2.append(f"LoverAvatarUrl=\"{result2[0][1]}\"")
            keyValue2.append(f"loverSessionKey=\"{result2[0][2]}\"")
            keyValue2.append(f"loverGender=\"{result2[0][3]}\"")
            keyValue2.append(f"loverNickName=\"{result2[0][4]}\"")
            ret = self.mySQLConnectionManage.update_data(tableName=userInfoTableName, openid=loverOpenid, keyValue=", ".join(keyValue2))
            if ret == -1:
                res_data["message"] = "update date fail."
                res_data["status_code"] = -1
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            res_data["message"] = "success"
            res_data["status_code"] = 200
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)


        @self.app.route('/getOpenid', methods=['POST'])
        def getOpenid():
            """
            获取用户的唯一标识openid和对应的seesionkey
            :param name:
            :return:
            """
            data = request.get_json()
            code = data.get('code')
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
            res_data = {}
            if responses.status_code == 200:
                res_json = json.loads(responses.text)
                openid = res_json['openid']
                sessionKey = res_json['session_key']
                result = self.mySQLConnectionManage.query_data(tableName=userInfoTableName, condition=f"WHERE Openid=\"{openid}\"")
                if result.__len__() == 0:
                    # (NickName, Openid, SessionKey, IsRegistered, isHasLover, LoverNickName, loverOpenid, loverSessionKey, AvatarUrl, LoverAvatarUrl, Gender)
                    self.mySQLConnectionManage.insert_data(tableName=userInfoTableName, data=("", openid, "", False, False, "", None, "", "", "", ""))
                res_data["openid"] = openid
                res_data["sessionKey"] = sessionKey
                res_data["message"] = "success"
                res_data["status_code"] = 200
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            else:
                res_data["message"] = "fail"
                res_data["status_code"] = 401
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)

        @self.app.route('/generatePresignedUrl', methods=['GET'])
        def generatePresignedUrl():
            """
            小程序上传文件时获取minio的presignedURL, 用于wx.uploadFile使用
            :param object_name: 上传到minio的文件名
            :return:presigned_url, 上传url
            """
            object_name = request.args.get('object_name')
            logger.info(f"received generate_presigned_url request, object_name is {object_name}")
            # 初始化 MinIO 客户端
            client = Minio(
                endpoint="yin2du.xin:9000",
                access_key="0VLq5WFevcJ5LHe9g9Ha",
                secret_key="C0Q2sFsMAPJ3q2vHzgwKAhaiXRpB9EbppAjnafUl",
                secure=True,
           )

            # Bucket 名称
            bucket_name = "xnloverservice"
            # object_name = "example.txt"  # 上传后的对象名称（文件名）

            # 生成一个有效期为 24 小时的 presigned PUT URL
            res_data = {}
            try:
                presigned_url = client.presigned_put_object(bucket_name, str(object_name),
                                                            expires=datetime.timedelta(hours=24))
                res_data["presigned_url"] = presigned_url
                res_data["status_code"] = 200
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            except S3Error as e:
                res_data["error"] = str(e)
                res_data["status_code"] = 500
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)

        # 设置允许上传的文件类型
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
        UPLOAD_FOLDER = 'uploads'

        # 检查文件扩展名是否允许
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        @self.app.route('/upload', methods=['POST'])
        def upload():
            logger.info(f"received a upload request.")
            # 检查请求中是否包含文件
            res_data = {}
            if 'file' not in request.files:
                res_data["error"] = 'No file part'
                res_data["status_code"] = 400
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            file = request.files['file']
            # 如果没有选择文件
            if file.filename == '':
                res_data["error"] = 'No selected file'
                res_data["status_code"] = 400
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            # 检查文件类型是否允许
            if file and allowed_file(file.filename):
                # 使用安全的文件名来保存
                filename = file.filename
                logger.info(f"filename is {filename}")
                filepath = os.path.join(UPLOAD_FOLDER, str(filename))
                logger.info(f"filepath is {filepath}")
                # 创建文件夹（如果没有的话）
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                # 保存文件
                file.save(filepath)
                minio_tos.upload(source_file=filepath, destination_file=filename)
                url = "https://yin2du.xin:9001/api/v1/buckets/xnloverservice/objects/download?preview=true&prefix=miniProgrameLover/" + str(filename)
                # 返回文件的保存路径或者相关信息
                res_data["message"] = "File uploaded successfully"
                res_data["file_url"] = url
                res_data["status_code"] = 200
                logger.info(f"Response: {res_data}")
                return jsonify(res_data)
            res_data["error"] = 'File type not allowed'
            res_data["status_code"] = 400
            logger.info(f"Response: {res_data}")
            return jsonify(res_data)

    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        # self.app.run(ssl_context=( 'sslFiles/fullchain.pem', 'sslFiles/privkey.pem'), host=self.host, port=self.port)
        self.app.run(host=self.host, port=self.port)
