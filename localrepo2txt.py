'''
@File    :   localrepo2txt.py
@Time    :   2024/04/12 01:02:06
@Author  :   CrissChan 
@Version :   1.0
@Site    :   https://blog.csdn.net/crisschan
@Desc    :   将本地代码打包成一个描述性文件，这里面包含了代码结构、代码详情，这样方便将整个项目直接上传到LLM，
             参考了https://github.com/Doriandarko/RepoToTextForLLM
'''

import os
from tqdm import tqdm

class LocalRepo2Txt(object):
    def __init__(self, repo_path):
        """
        初始化LocalRepo2Txt类，设置仓库路径。
        
        :param repo_path: 本地仓库的路径
        """
        self.repo_path = repo_path

    def get_repo_txt(self) -> str:
        """
        获取本地仓库的文本描述，包括结构和文件内容，并保存到一个文本文件中。
        
        :return: 输出文件的名称，如果出错则返回None
        """
        try:
            repo_name, instructions, repo_structure, file_contents = self.get_local_repo_contents()
            output_filename = f'{repo_name}_contents.txt'
            if  os.path.exists(output_filename):
                os.remove(output_filename)
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(instructions)
                f.write(repo_structure)
                f.write('\n\n')
                f.write(file_contents)
            return output_filename
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please check the repository path and try again.")
            return None

    def traverse_local_repo_iteratively(self):
        """
        迭代遍历本地仓库，获取其目录结构。
        
        :return: 仓库的目录结构字符串
        """
        structure = ""
        dirs_to_visit = [self.repo_path]
        dirs_visited = set()

        while dirs_to_visit:
            current_path = dirs_to_visit.pop()
            dirs_visited.add(current_path)
            for entry in tqdm(os.scandir(current_path), desc=f"Processing {current_path}", leave=False):
                if entry.is_dir():
                    if entry.path not in dirs_visited:
                        structure += f"{entry.path}/\n"
                        dirs_to_visit.append(entry.path)
                else:
                    structure += f"{entry.path}\n"
        return structure

    def get_local_file_contents_iteratively(self):
        """
        迭代获取本地仓库中所有文件的内容，跳过二进制文件。
        
        :return: 文件内容的字符串
        """
        file_contents = ""
        dirs_to_visit = [self.repo_path]
        dirs_visited = set()
        binary_extensions = [
            # 二进制文件扩展名列表
            '.exe', '.dll', '.so', '.a', '.lib', '.dylib', '.o', '.obj',
            # 压缩文件
            '.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.bz2', '.gz', '.xz', '.z', '.lz', '.lzma', '.lzo', '.rz', '.sz', '.dz',
            # 应用程序文件
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
            # 媒体文件
            '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.wav', '.flac', '.ogg', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.m4a', '.aac',
            # 虚拟机和容器镜像
            '.iso', '.vmdk', '.qcow2', '.vdi', '.vhd', '.vhdx', '.ova', '.ovf',
            # 数据库文件
            '.db', '.sqlite', '.mdb', '.accdb', '.frm', '.ibd', '.dbf',
            # Java相关文件
            '.jar', '.class', '.war', '.ear', '.jpi',
            # Python字节码和包
            '.pyc', '.pyo', '.pyd', '.egg', '.whl',
            # 其他重要扩展名
            '.deb', '.rpm', '.apk', '.msi', '.dmg', '.pkg', '.bin', '.dat', '.data',
            '.dump', '.img', '.toast', '.vcd', '.crx', '.xpi', '.lockb', 'package-lock.json', '.svg',
            '.eot', '.otf', '.ttf', '.woff', '.woff2',
            '.ico', '.icns', '.cur',
            '.cab', '.dmp', '.msp', '.msm',
            '.keystore', '.jks', '.truststore', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.csr',
            '.key', '.pub', '.sig', '.pgp', '.gpg',
            '.nupkg', '.snupkg', '.appx', '.msix', '.msp', '.msu',
            '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
            '.ko', '.sys', '.elf',
            '.swf', '.fla', '.swc',
            '.rlib', '.pdb', '.idb', '.pdb', '.dbg',
            '.sdf', '.bak', '.tmp', '.temp', '.log', '.tlog', '.ilk',
            '.bpl', '.dcu', '.dcp', '.dcpil', '.drc',
            '.aps', '.res', '.rsrc', '.rc', '.resx',
            '.prefs', '.properties', '.ini', '.cfg', '.config', '.conf',
            '.DS_Store', '.localized', '.svn', '.git', '.gitignore', '.gitkeep',
        ]

        while dirs_to_visit:
            current_path = dirs_to_visit.pop()
            dirs_visited.add(current_path)
            for entry in tqdm(os.scandir(current_path), desc=f"Downloading {current_path}", leave=False):
                if entry.is_dir():
                    if entry.path not in dirs_visited:
                        dirs_to_visit.append(entry.path)
                else:
                    # 检查文件扩展名是否为二进制文件
                    if any(entry.name.endswith(ext) for ext in binary_extensions):
                        file_contents += f"File: {entry.path}\nContent: Skipped binary file\n\n"
                    else:
                        file_contents += f"File: {entry.path}\n"
                        try:
                            with open(entry.path, 'r', encoding='utf-8') as file:
                                file_contents += f"Content:\n{file.read()}\n\n"
                        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
                            file_contents += "Content: Skipped due to decoding error or file not found\n\n"
        return file_contents

    def get_local_repo_contents(self):
        """
        获取本地仓库的完整内容，包括目录结构和文件内容。
        
        :return: 仓库名称、说明、目录结构和文件内容
        """
        repo_name = os.path.basename(self.repo_path)

        print(f"Fetching repository structure for: {repo_name}")
        repo_structure = f"Repository Structure: {repo_name}\n"
        repo_structure += self.traverse_local_repo_iteratively()

        # 将绝对路径替换为相对路径
        repo_structure = repo_structure.replace(self.repo_path, '.')

        print(f"\nFetching file contents for: {repo_name}")
        file_contents = self.get_local_file_contents_iteratively()

        instructions = "Use the files and contents provided below to complete this analysis:\n\n"

        return repo_name, instructions, repo_structure, file_contents

if __name__ == '__main__':
    # 创建LocalRepo2Txt对象并生成仓库文本描述
    local_repo_2_txt = LocalRepo2Txt('/Users/crisschan/workspace/PySpace/karma/target_project')
    print(local_repo_2_txt.get_repo_txt())
