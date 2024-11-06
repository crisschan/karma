import os
import shutil
import subprocess
import json
import re


class LineTrace(object):
  
    def __init__(self, source_dir: str, destination_dir: str, modi_file_path: str, uncover_codeline_number:int):
        """
        初始化 Line2Api 类的实例。
        :param source_dir: 源目录的路径
        :param destination_dir: 目标目录的路径
        :param modi_file_path: 已修改的文件路径
        :param line_number: 已修改的行号
        """
        # 初始化源目录和目标目录
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.modi_file_path = source_dir+"/"+modi_file_path
        self.uncover_codeline_number = uncover_codeline_number
        # self.line_number =   
    def _find_uncover_code(self):
        """
        获取未覆盖的代码行
        :return: 未覆盖的代码行
        """
        with open(self.modi_file_path, 'r') as f:
            lines = f.readlines()
        return lines[self.uncover_codeline_number - 1].strip()

        # 如果未找到匹配的代码行，返回 (None, None)
        return None
    def need_api(self) -> json:
        """
        处理 API 需求的主要逻辑，包括复制文件、修改文件和编译项目。
        :return: 返回 API 结果{'method': ' com/demo/bankapp/service/concretions/WealthService.makeWealthExchange(Long, String, BigDecimal, boolean)void', 'API': '[http]|/transaction/create', 'function': 'makeWealthExchange(Long userId, String currency, BigDecimal amount, boolean isBuying)', 'ine_number': 70}
        """
        self.uncover_code = self._find_uncover_code()
        # 复制文件
        self.__copy_file()

        # 修改指定文件的特定行
        self.__modify_file(self.modi_file_path, self.uncover_codeline_number)
        # 编译项目
        result = self.__findtheapi()
        result['uncover_code'] = self.uncover_code
        result['uncover_codeline_number'] = self.uncover_codeline_number
        
        return result
    def __copy_file(self):
        """
        复制源目录中的文件到目标目录，删除已存在的目标目录。
        """
        # 切换到上级目录
        # os.chdir('..')  
        # 删除目标目录（如果存在）
        if os.path.exists(self.destination_dir):
            shutil.rmtree(self.destination_dir)
        
        # 创建目标目录
        os.makedirs(self.destination_dir, exist_ok=True)

        # 遍历源目录中的所有文件
        for filename in os.listdir(self.source_dir):
            print(filename)
            source_file = os.path.join(self.source_dir, filename)
            destination_file = os.path.join(self.destination_dir, filename)
            
            # 复制文件
            if os.path.isfile(source_file):
                shutil.copy2(source_file, destination_file)
            # 复制文件夹
            elif os.path.isdir(source_file):
                shutil.copytree(source_file, destination_file)

    def __modify_file(self, file_path: str, line_number: int, new_code="Integer abc = 1;"):
        """
        修改指定文件的特定行，添加新代码。
        :param file_path: 文件路径
        :param line_number: 要修改的行号
        :param new_code: 新代码内容
        """
        # 读取文件内容
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # 在指定行后添加新代码
        lines[line_number - 1] = lines[line_number - 1].rstrip() + new_code + '\n'

        # 写回文件
        with open(file_path, 'w') as file:
            file.writelines(lines)

    def __findtheapi(self) -> json:
        """
        编译项目并运行静态链分析，返回分析结果。
        :return: 返回分析结果的 JSON 格式
        """
        print(os.getcwd())
        # 切换到目标目录
        os.chdir(self.destination_dir)  
        # 运行 Maven 编译命令
        os.system('mvn compile')  
        # 切换到静态链分析目录
        os.chdir('../static_chain_anlysis')  
        # 运行 Java 命令并捕获输出
        result = subprocess.run(['java', '-jar', 'static-chain-analysis-1.0-SNAPSHOT-jar-with-dependencies.jar'], capture_output=True, text=True)
        func2api = result.stdout.replace("\n", "")  # 处理命令输出
        
        # 切换回上级目录
        os.chdir('..')
        return json.loads(func2api)  # 将输出格式化为 JSON  
        # return func2api
        