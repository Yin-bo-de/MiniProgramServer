import http.server
import json
import ssl
from loguru import logger

from commentRecord.readComment import ReadComment


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self): #处理 GET 请求。
        # 获取请求路径
        path = self.path
        logger.info("receviced GET request," + path)
        # 根据不同的 URI 处理请求
        if path == '/comment':
            readComment = ReadComment()
            # readComment.read(param=) # 从 request中获取姓名和date（“年-月”）

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Hello, this is the /hello endpoint!")


    def do_POST(self):
        """处理 POST 请求"""
        content_length = self.headers.get('Content-Length', None)
        if content_length:
            content_length = int(content_length)
            body = self.rfile.read(content_length)  # 读取指定长度的数据
        else:
            # 没有 Content-Length 且不是 chunked 编码，处理其他逻辑
            body = self.rfile.read()
        path = self.path
        logger.info("receviced POST request," + path)
        logger.info(body)

        try:
            if path == '/comment':
                # 尝试将数据解析为 JSON
                data = json.loads(body)
                logger.critical(data)
                # 发送响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                # 返回处理后的数据（这里简单地返回接收到的数据）
                response = {
                    'status': 'success',
                    'received_data': data
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))

        except json.JSONDecodeError:
            # 如果数据无法解析为 JSON，返回 400 错误
            logger.error("uri error.")
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"400 Bad Request: Invalid JSON")


def startServer():
    logger.info("lover server start.")
    PORT = 443
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='./example.crt', keyfile="./example.key")

    ciphers = ""
    ciphers += "ECDHE-ECDSA-AES128-GCM-SHA256:"
    ciphers += "ECDHE-ECDSA-CHACHA20-POLY1305:"
    ciphers += "ECDHE-RSA-CHACHA20-POLY1305:"
    ciphers += "ECDHE-RSA-AES128-GCM-SHA256:"
    context.set_ciphers(ciphers)

    httpd = http.server.HTTPServer(('0.0.0.0', PORT), MyHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    logger.info(f"Server started at http://localhost:{PORT}")
    httpd.serve_forever()

    # with http.server.HTTPServer(("", PORT), MyHandler) as server:  # 用于创建 TCP 服务监听指定端口。"" 表示绑定到所有可用的网络接口。
    #     logger.info(f"Server started at http://localhost:{PORT}")
    #     server.serve_forever()  # 会让服务器持续运行，直到手动停止。

def initLog():
    # 输出到文件，并且支持日志轮换（每天一个日志文件）
    logger.add("log/app.log", rotation="00:00:00")  # 每天午夜自动生成新日志文件
    # commentRecord记录存储到这里
    logger.add("commentRecord/comment_{time:YYYY-MM}.log", level="CRITICAL", rotation="1 month", retention="6 months", format="{time:YYYY-MM-DD HH:mm:ss.SSS} {message}")
    # 输出日志到文件，最大文件大小为 10MB，最多保留 3 个备份
    # logger.add("app.log", rotation="10 MB", retention="3 files")

if __name__ == "__main__":
    initLog()
    startServer()