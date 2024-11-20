# MiniProgram

#获取openssl
openssl req -newkey rsa:2048 -nodes -keyout example.key -x509 -days 365 -out example.crt

#查看ssl
openssl x509 -in example.crt -text -noout