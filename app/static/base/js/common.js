((window, document) => {
    'use strict';

    window.MyFunction = {
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

    window.globalVariable = {
        fileTypeIconMap: {
            'dir': 'bi bi-folder2',
            'package': 'bi bi-file-zip',
            'video': 'bi bi-camera-video',
            'image': 'bi bi-image',
            'audio': 'bi bi-music-note-beamed',
            'text': 'bi bi-file-text',
            'unknown': 'bi bi-question-square'
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
