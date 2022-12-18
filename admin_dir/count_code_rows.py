import os.path
from collections import deque
from config import BASE_PATH


def path_iter(root_node: list, root_path: str) -> iter:
    q = deque()
    q.append((root_path, root_node))
    while q:
        current_path, current_tree = q.popleft()
        for node in current_tree:
            if not isinstance(node, dict):
                yield os.path.realpath(os.path.join(current_path, node))
                continue
            sub_path, sub_node = node.popitem()
            q.append((os.path.realpath(os.path.join(current_path, sub_path)), sub_node))


def count_rows(filepath: str) -> int:
    rows = 0
    with open(filepath, 'r', encoding='UTF-8') as file:
        line = file.readline()
        while line:
            if line != '\n':
                rows = rows + 1
            line = file.readline()
        file.close()
    return rows


def count_project_rows(data: list, root_path: str) -> tuple:
    result = []
    total_rows = 0
    for path in path_iter(data, root_path):
        rows = count_rows(path)
        total_rows = total_rows + rows
        for i, v in enumerate(result):
            if v[0] < rows:
                result.insert(i, (rows, path))
                break
        else:
            result.append((rows, path))

    return total_rows, result


if __name__ == '__main__':
    j = [
        {
            'app': [
                {
                    'auth': [
                        '__init__.py',
                        'views.py'
                    ]
                },
                {
                    'main': [
                        '__init__.py',
                        'views.py'
                    ]
                },
                {
                    'static': [
                        {
                            'auth': [
                                {
                                    'js': [
                                        'user_manage.js',
                                        'visible_dir.js'
                                    ]
                                },
                                {
                                    'sass': [
                                        'user_manage.scss',
                                        'visible_dir.scss'
                                    ]
                                }
                            ]
                        },
                        {
                            'base': [
                                {
                                    'js': [
                                        'base.js',
                                        'common.js',
                                        'error.js'
                                    ]
                                },
                                {
                                    'sass': [
                                        'base.scss'
                                    ]
                                }
                            ]
                        },
                        {
                            'main': [
                                {
                                    'js': [
                                        'index.js'
                                    ]
                                },
                                {
                                    'sass': [
                                        'index.scss'
                                    ]
                                }
                            ]
                        },
                        '_mixin.scss',
                        '_variable.scss'
                    ]
                },
                {
                    'templates': [
                        {
                            'auth': [
                                'user_manage.html',
                                'visible_dir.html'
                            ]
                        },
                        {
                            'base': [
                                '404.html',
                                '500.html',
                                'base.html',
                                'macro.html'
                            ]
                        },
                        {
                            'main': [
                                'index.html'
                            ]
                        }
                    ]
                },
                '__init__.py',
                'middleware.py',
                'model.py',
                'path_untils.py',
                'untils.py'
            ]
        },
        'config.py',
        'file_server.py'
    ]

    count, info = count_project_rows(j, BASE_PATH)
    print('{}\t\ttotal'.format(count))
    for rows, path in info:
        print('{}\t\t{}'.format(rows, path))
