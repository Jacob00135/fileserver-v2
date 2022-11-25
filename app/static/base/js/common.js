((window, document) => {
    'use strict';

    window.MyRoute = {
        main: {
            download: (path) => {
                return '/download?path=' + path;
            }
        }
    };

    window.MyFunction = {
        inArray: (array, value) => {
            for (let i = 0; i < array.length; i++) {
                if (array[i] === value) {
                    return true;
                }
            }
            return false;
        },

        alert: (title = '警告', message = '') => {
            const modal = document.getElementById('hint-modal');
            modal.querySelector('.modal-title').innerHTML = title;
            modal.querySelector('.modal-body').innerHTML = message;
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        },

        splitPath: (path) => {
            // 分割一个绝对路径，返回目录路径和文件路径

            // 寻找\\
            let index = -1;
            for (let i = path.length - 1; i >= 0; i--) {
                if (path.charAt(i) === '\\') {
                    index = i;
                    break;
                }
            }

            // 如果没有找到\\
            if (index === -1) {
                return ['.', path];
            }

            // 如果找到了\\
            return [
                path.slice(0, index),
                path.slice(index + 1)
            ];
        },

        strip: (string, char) => {
            let start = 0;
            let end = string.length - 1;
            while (string.charAt(start) === char) {
                start = start + 1;
            }
            while (string.charAt(end) === char) {
                end = end - 1;
            }
            return string.slice(start, end + 1);
        },

        concatPath: (path1, path2) => {
            return MyFunction.strip(path1, '\\') + '\\' + MyFunction.strip(path2, '\\');
        }
    };

    window.MyAJAX = {
        getJson: (url) => {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('get', url, true);
                xhr.send();
                xhr.addEventListener('readystatechange', (e) => {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        const data = JSON.parse(xhr.responseText);
                        if (data.status === 1) {
                            resolve(data);
                        } else {
                            reject(data);
                        }
                    }
                });
            });
        },

        getFile: (url) => {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('get', url, true);
                xhr.send();
                xhr.responseType = 'blob';
                xhr.addEventListener('readystatechange', (e) => {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            resolve(xhr.response);
                        } else {
                            reject(xhr);
                        }
                    }
                });
            });
        }
    };

    // 复制按钮组件
    document.querySelectorAll('.copy-btn').forEach((btn) => {
        const copyIcon = btn.querySelector('.copy-icon');
        const input = document.querySelector(btn.getAttribute('data-control'));
        btn.addEventListener('click', (e) => {
            input.select();
            document.execCommand('copy');
            copyIcon.classList.remove('bi-clipboard');
            copyIcon.classList.add('bi-check2');
            setTimeout(() => {
                copyIcon.classList.remove('bi-check2');
                copyIcon.classList.add('bi-clipboard');
            }, 2000);
        });
    });

})(window, document);
