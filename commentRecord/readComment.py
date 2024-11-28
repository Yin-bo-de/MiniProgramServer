import os


class ReadComment:
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.commentRecordLogDir = 'comment.log'
        self.folder_path = os.getcwd()

    def read(self, param):
        # 获取文件夹内所有文件名（不包含子目录）
        files = [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f))]
        result = ''
        # 读取每个文件的内容
        for file_name in files:
            file_path = os.path.join(self.folder_path, file_name)
            if file_path.endswith(".log") and param.date in file_path: # 找到对应日期的文件
                with open(file_path, 'r') as file:
                    content = file.readline()
                    while content:
                        if param.name in content: # 找到对应的人的内容，并将其组装成json
                            result += content + "\n"
                            # print(f"内容来自 {file_name}: \n{content}")
                        content = file.readline()
                    return result

    def write(self, param):
        pass