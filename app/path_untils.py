import os
from collections import OrderedDict


def get_file_size(file_path: str or int, result: str = 'str') -> str or int:
    # 检查参数，如果是文件/目录路径，则计算文件/目录大小
    if isinstance(file_path, str):
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
        else:
            size = 0
            for father, dir_names, filenames in os.walk(file_path):
                for filename in filenames:
                    size = size + os.path.getsize(os.path.join(father, filename))
    elif isinstance(file_path, int):
        size = file_path
    else:
        raise ValueError('file_path参数类型只能是`str`或`int`！')

    # 检查返回值类型
    if result == 'int':
        return size
    elif result != 'str':
        raise ValueError('result参数只能是`str`或`int`')

    # 计算大小
    unit_list = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size >= 1024:
        size = size / 1024
        i = i + 1
    return '{}{}'.format(round(size, 2), unit_list[i])


def is_legal_path(path: str) -> bool:
    if path.find('/') == -1 and path.find('\\') == -1:
        return False
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return False
    return True


def get_file_type(filepath: str) -> str:
    i = filepath.rfind('.')
    if i == -1:
        return 'unknown'
    return FilePath.extension_type_map.get(filepath[i + 1:], 'unknown')


class Path(object):

    def __init__(self, path: str):
        if not is_legal_path(path):
            raise ValueError('路径不合法：{}'.format(path))
        self.path = os.path.realpath(path)

    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self.path)


class MountPath(Path):

    def __init__(self, path: str):
        super(MountPath, self).__init__(path)
        self.dirname = self.path
        self.type = 'dir'
        self.size = ''

        self.father_path = None
        self.father = None
        self.__children = None

        # 用于统一获取属性
        self.name = self.dirname[:-1]

        # 用于指定读取子文件的区间段
        self.read_section = (0, None)
        self.children_sort = True

    @staticmethod
    def is_upper():
        """判断path是否是上层路径"""
        return False

    @staticmethod
    def is_father():
        """判断path是否是真上级路径"""
        return False

    @property
    def children(self):
        if self.__children is None:
            self.__children = get_children(self.path, self.read_section, self.children_sort)
        return self.__children


class DirPath(Path):

    def __init__(self, path: str):
        super(DirPath, self).__init__(path)

        self.dirname = os.path.basename(self.path)
        self.type = 'dir'
        self.size = ''

        self.father_path = os.path.dirname(self.path)
        self.__father = None

        self.mount_path = self.path[:self.path.find(':') + 2]
        self.mount = MountPath(self.mount_path)

        self.__children = None

        # 用于统一获取属性
        self.name = self.dirname

        # 用于指定读取子文件的区间段
        self.read_section = (0, None)
        self.children_sort = True

    @property
    def father(self):
        if self.__father is None:
            if os.path.ismount(self.father_path):
                self.__father = MountPath(self.father_path)
            else:
                self.__father = DirPath(self.father_path)
        return self.__father

    @property
    def children(self):
        if self.__children is None:
            self.__children = get_children(self.path, self.read_section, self.children_sort)
        return self.__children

    def is_upper(self, path: str) -> bool:
        """判断path是否是上层路径"""
        if not is_legal_path(path):
            return False
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        if path == self.path:
            return False
        return os.path.commonpath((path, self.path)) == path

    def is_father(self, path: str) -> bool:
        """判断path是否是真上级路径"""
        if not is_legal_path(path):
            return False
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        return path == self.father_path


class FilePath(Path):

    extension_type_map = {
        'rar': 'package',
        'zip': 'package',
        '7z': 'package',
        'gz': 'package',
        'tar': 'package',
        'mp4': 'video',
        'm4v': 'video',
        'mkv': 'video',
        'webm': 'video',
        'mov': 'video',
        'avi': 'video',
        'wmv': 'video',
        'mpg': 'video',
        'flv': 'video',
        'mpeg': 'video',
        'rm': 'video',
        'ram': 'video',
        'rmvb': 'video',
        'jpg': 'image',
        'png': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'webp': 'image',
        'ico': 'image',
        'bmp': 'image',
        'psd': 'image',
        'dwg': 'image',
        'xcf': 'image',
        'jpx': 'image',
        'apng': 'image',
        'cr2': 'image',
        'tif': 'image',
        'jxr': 'image',
        'heic': 'image',
        'mp3': 'audio',
        'wav': 'audio',
        'm4a': 'audio',
        'flac': 'audio',
        'aac': 'audio',
        'ogg': 'audio',
        'mid': 'audio',
        'amr': 'audio',
        'aiff': 'audio',
        'txt': 'text',
        'py': 'text',
        'js': 'text',
        'ipynb': 'text',
        'ini': 'text',
        'css': 'text',
        'scss': 'text',
        'sass': 'text',
        'html': 'text',
        'xml': 'text',
        'json': 'text',
        'java': 'text',
        'c': 'text',
        'cpp': 'text',
        'md': 'text'
    }

    def __init__(self, path: str):
        super(FilePath, self).__init__(path)

        self.full_filename = os.path.basename(self.path)
        self.filename = None
        self.extension = None
        self.__set_extension()
        self.type = self.extension_type_map.get(self.extension, 'unknown')
        self.size = get_file_size(path)

        self.father_path = os.path.dirname(self.path)
        self.__father = None

        self.mount_path = self.path[:self.path.find(':') + 2]
        self.mount = MountPath(self.mount_path)

        # 用于统一获取属性
        self.name = self.full_filename

    def __set_extension(self) -> None:
        i = self.full_filename.rfind('.')
        if i == -1:
            self.extension = ''
            self.filename = self.full_filename
        else:
            self.extension = self.full_filename[i + 1:]
            self.filename = self.full_filename[:i]

    @property
    def father(self):
        if self.__father is None:
            if os.path.ismount(self.father_path):
                self.__father = MountPath(self.father_path)
            else:
                self.__father = DirPath(self.father_path)
        return self.__father

    def is_upper(self, path: str) -> bool:
        """判断path是否是上层路径"""
        if not is_legal_path(path):
            return False
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        return os.path.commonpath((path, self.path)) == path

    def is_father(self, path: str) -> bool:
        """判断path是否是真上级路径"""
        if not is_legal_path(path):
            return False
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        return path == self.father_path


def get_children(path: str, read_section: tuple = (0, None), sort_by_type: bool = True) -> list[DirPath or FilePath]:
    file_list = os.listdir(path)
    if sort_by_type:
        # 获取目录中所有子文件的文件名，并按照文件类型进行排序
        file_map = OrderedDict({
            'dir': [],
            'package': [],
            'video': [],
            'image': [],
            'audio': [],
            'text': [],
            'unknown': []
        })
        for filename in os.listdir(path):
            file_path = os.path.realpath(os.path.join(path, filename))
            file_type = 'dir' if os.path.isdir(file_path) else get_file_type(file_path)
            file_map[file_type].append(filename)
        file_list = []
        while file_map:
            file_list.extend(file_map.popitem(False)[1])

    # 实例化
    children = []
    start, end = read_section
    for filename in file_list[start:end]:
        child_path = os.path.realpath(os.path.join(path, filename))
        if os.path.isdir(child_path):
            children.append(DirPath(child_path))
        elif os.path.isfile(child_path):
            children.append(FilePath(child_path))
        else:
            raise TypeError('既不是目录也不是文件：{}'.format(child_path))
    return children


def create_path_object(visible_dir_list: list) -> list:
    object_list = []
    for visible_dir in visible_dir_list:
        if os.path.ismount(visible_dir.dir_path):
            obj = MountPath(visible_dir.dir_path)
        else:
            obj = DirPath(visible_dir.dir_path)
        object_list.append(obj)
    return object_list


def search_file_on_dir(dir_path: str, keyword: str) -> iter:
    for father, sub_dirs, sub_files in os.walk(dir_path):
        for sub_dir in sub_dirs:
            start = sub_dir.find(keyword)
            if start >= 0:
                yield 'dir', start, sub_dir, os.path.realpath(os.path.join(father, sub_dir))
        for sub_file in sub_files:
            start = sub_file.find(keyword)
            if start >= 0:
                file_path = os.path.realpath(os.path.join(father, sub_file))
                yield get_file_type(file_path), start, sub_file, file_path


if __name__ == '__main__':
    pass
