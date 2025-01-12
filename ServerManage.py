


"""
功能描述：lover server manage类
参数：host，监听域名，port监听端口
"""
import datetime
import json
import os

import requests
from flask import jsonify, request, Flask
from loguru import logger
from minio import Minio, S3Error

from Utils import minio_tos
from dataBaseTableManager import userInfoTableName, commentTableName


class ServerManage():
    def __init__(self, mySQLConnectionManage, host='127.0.0.1', port=8081):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.mySQLConnectionManage = mySQLConnectionManage


        @self.app.route('/getComment', methods=['GET'])
        def getComment():
            """
            监听小程序的获取留言记录的接口
            """
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


        @self.app.route('/postComment', methods=['POST'])
        def postComment():
            """
            监听小程序的发表留言记录的接口
            """
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


        @self.app.route('/userRegister', methods=['POST'])
        def userRegister():
            """
            用户点击头像进行注册的接口，更新IsRegistered、gender、avatarUrl
            :param name:
            :return:
            """
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


        @self.app.route('/getUserRigisterStatus', methods=['POST'])
        def getUserRigisterStatus():
            """
            登陆小程序界面时，请求当前用户的注册状态，并获取对应的头像url展示
            :param name:
            :return:
            """
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


        # todo
        @self.app.route('/loverInvite', methods=['POST'])
        def loverInvite():
            """
            邀请恋人加入，将恋人的数据更新到自己的数据表，并更新恋人数据表
            :param name:
            :return:
            """
            data = request.get_json()
            logger.info(f"receive loverInvite request: data: {data}")

            return jsonify(message="success",
                           status_code=200)


        @self.app.route('/getOpenid', methods=['POST'])
        def getOpenid():
            """
            获取用户的唯一标识openid和对应的seesionkey
            :param name:
            :return:
            """
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

        @self.app.route('/generatePresignedUrl', methods=['GET'])
        def generatePresignedUrl():
            """
            小程序上传文件时获取minio的presignedURL，用于wx.uploadFile使用
            :param object_name: 上传到minio的文件名
            :return:presigned_url，上传url
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
            try:
                presigned_url = client.presigned_put_object(bucket_name, object_name,
                                                            expires=datetime.timedelta(hours=24))
                return jsonify(presigned_url=presigned_url, status_code=200)
            except S3Error as e:
                return jsonify(error=str(e), status_code=500)

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
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
            # 如果没有选择文件
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            # 检查文件类型是否允许
            if file and allowed_file(file.filename):
                # 使用安全的文件名来保存
                filename = file.filename
                logger.info(f"filename is {filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                logger.info(f"filepath is {filepath}")
                # 创建文件夹（如果没有的话）
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                # 保存文件
                file.save(filepath)
                minio_tos.upload(source_file=filepath, destination_file=filename)
                url = "https://yin2du.xin:9001/api/v1/buckets/xnloverservice/objects/download?preview=true&prefix=miniProgrameLover/" + filename
                # 返回文件的保存路径或者相关信息
                return jsonify(message="File uploaded successfully", file_url=url, status_code=200)
            return jsonify({'error': 'File type not allowed'}), 400

    def run(self):
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        # self.app.run(ssl_context=( 'sslFiles/fullchain.pem', 'sslFiles/privkey.pem'), host=self.host, port=self.port)
        self.app.run(host=self.host, port=self.port)
