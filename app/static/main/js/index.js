((window, document) => {
    'use strict';

    // 复制当前目录绝对路径
    (() => {
        const btn = document.getElementById('copy-current-dir-path');
        if (!btn) return undefined;
        const copyIcon = btn.querySelector('.copy-icon');

        btn.addEventListener('click', (e) => {
            // 复制当前目录的绝对路径
            const path = btn.getAttribute('data-current-dir-path');
            const input = document.createElement('input');
            input.value = path;
            input.style.position = 'absolute';
            input.style.top = '-9999px';
            input.style.left = '-9999px';
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);

            // 图标变化
            copyIcon.classList.remove('bi-clipboard');
            copyIcon.classList.add('bi-check2');
            setTimeout(() => {
                copyIcon.classList.remove('bi-check2');
                copyIcon.classList.add('bi-clipboard');
            }, 2000);
        });
    })();

    // 查看完整文件名
    (() => {
        const modal = document.getElementById('full-file-name-modal');
        const show = modal.querySelector('.show-file-name');

        // 弹出模态框
        document.querySelectorAll('#app .file-list .action-dropdown .full-file-name').forEach((a) => {
            a.addEventListener('click', (e) => {
                show.value = a.getAttribute('data-file-name');
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 删除文件
    (() => {
        const modal = document.getElementById('delete-file-modal');
        const form = document.forms['delete-file'];

        document.querySelectorAll('#app .file-list .action-dropdown .remove').forEach((a) => {
            a.addEventListener('click', (e) => {
                form.querySelector('.file-name').textContent = a.getAttribute('data-file-name');
                form.querySelector('input[name="path"]').setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 重命名文件
    (() => {
        const modal = document.getElementById('rename-file-modal');
        const form = document.forms['rename-file'];

        document.querySelectorAll('#app .file-list .action-dropdown .rename').forEach((a) => {
            a.addEventListener('click', (e) => {
                const filePath = a.getAttribute('data-file-path');
                const fileName = a.getAttribute('data-file-name');
                form.querySelector('input[name="path"]').setAttribute('value', filePath);
                form.querySelector('.source-file-name').setAttribute('value', fileName);
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 移动文件
    (() => {
        const modal = document.getElementById('move-file-modal');
        const form = document.forms['move-file'];
        const filePathInput = form.querySelector('input[name="source-file-path"]');

        document.querySelectorAll('#app .file-list .action-dropdown .move').forEach((a) => {
            a.addEventListener('click', (e) => {
                filePathInput.setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 复制文件
    (() => {
        const modal = document.getElementById('copy-file-modal');
        const form = document.forms['copy-file'];
        const filePathInput = form.querySelector('input[name="source-file-path"]');

        document.querySelectorAll('#app .file-list .action-dropdown .copy').forEach((a) => {
            a.addEventListener('click', (e) => {
                filePathInput.setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 上传文件
    (() => {
        const form = document.forms['upload-file'];
        const fileInput = form.querySelector('input[name="file"]');
        const submitBtn = form.querySelector('[type="submit"]');
        const progressBox = form.querySelector('.progress');
        const progress = form.querySelector('.progress .progress-bar');
        const errorHint = form.querySelector('.alert');
        const errorTextNode = form.querySelector('.alert .text');
        const closeBtn = form.querySelector('.alert .btn-close');
        const maxFileSize = parseInt(fileInput.getAttribute('data-max-size'));
        const uploadFileHintInfo = errorTextNode.getAttribute('data-upload-file-hint-info');

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // 检查文件大小
            const file = fileInput.files[0];
            if (file.size > maxFileSize) {
                errorTextNode.innerHTML = uploadFileHintInfo;
                errorHint.classList.remove('d-none');
                return undefined;
            }

            // 提交文件前，先把警告框隐藏、上传按钮禁用
            submitBtn.setAttribute('disabled', '');
            errorHint.classList.add('d-none');

            // ajax提交文件
            const url = form.getAttribute('action');
            const formData = new FormData(form);
            const xhr = new XMLHttpRequest();

            // 上传文件进度
            progressBox.classList.remove('d-none');
            progress.setAttribute('aria-valuenow', '0');
            progress.style.width = '0';
            progress.innerHTML = '';
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const rate = Math.floor((e.loaded / e.total) * 100);
                    progress.setAttribute('aria-valuenow', String(rate));
                    progress.style.width = rate + '%';
                    if (rate > 99) {
                        progress.innerHTML = '上传完毕，正在保存文件，请等待...';
                    } else {
                        progress.innerHTML = rate + '%';
                    }
                }
            });

            xhr.open('post', url, true);
            xhr.send(formData);

            // 处理响应
            xhr.addEventListener('readystatechange', (e) => {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    if (data.status === 0) {
                        errorTextNode.innerHTML = data.message;
                        errorHint.classList.remove('d-none');
                        submitBtn.removeAttribute('disabled');
                        progressBox.classList.add('d-none');
                    } else {
                        location.reload();
                    }
                }
            });
        });

        closeBtn.addEventListener('click', (e) => {
            errorHint.classList.add('d-none');
        });
    })();

    // 预览目录
    (() => {
        const modal = document.getElementById('preview-dir-modal');
        const root = modal.querySelector('.struct .root');

        document.querySelectorAll('#app .file-list .action-dropdown .preview-dir').forEach((a) => {
            a.addEventListener('click', (e) => {
                // 初始化模态框
                showLoading();
                hiddenStructFail();
                clearStruct();
                (new bootstrap.Modal(modal, {keyboard: false})).show();

                // 请求目录结构
                const url = a.getAttribute('data-href');
                MyAJAX.getJson(url).then(
                    (data) => {
                        buildStruct(data.result);
                        hiddenLoading();
                    },
                    (data) => {
                        hiddenLoading();
                        showStructFail(data.message);
                    }
                );
            });
        });
        modal.querySelector('.fold-all-btn').addEventListener('click', foldAll);
        modal.querySelector('.unfold-all-btn').addEventListener('click', unfoldAll);

        // region 旧的下载目录方案
        /*
        modal.querySelector('.download').addEventListener('click', (e) => {
            disabledDownload();
            modal.querySelector('.download-info').classList.remove('d-none');

            // 初始化
            const rootPath = root.struct[0]['path'];
            let z = new JSZip();
            let promise = new Promise((resolve, reject) => {
                resolve(null);
            });
            root.i = 0;

            function promiseFinally() {
                // 判断是否应该退出
                root.i = root.i + 1;
                if (root.i >= root.struct.length) {
                    compressStatus();
                    return z.generateAsync({type: 'blob'});
                }

                // 判断本次要归档的是否是目录
                const path = root.struct[root.i]['path'];
                if (root.struct[root.i]['type'] === 'dir') {
                    z.folder(path);
                    return new Promise((resolve, reject) => {
                        resolve(null);
                    });
                }

                // 请求文件
                const url = MyRoute.main.download(MyFunction.concatPath(rootPath, path));
                downloadStatus(path);
                return MyAJAX.getFile(url);
            }

            // 逐个请求文件
            for (let i = 0; i < root.struct.length; i++) {
                promise = promise.then(
                    (response) => {
                        // 处理上一次promise的结果
                        if (response) {
                            const path = root.struct[root.i]['path'];
                            z.file(path, response);

                            // 提示下载成功，添加“√”
                            // 寻找下载失败的文件项目
                            let failItem;
                            const itemArr = root.querySelectorAll('.item');
                            for (let i = 0; i < itemArr.length; i++) {
                                if (itemArr[i].getAttribute('data-path') === path) {
                                    failItem = itemArr[i];
                                    break;
                                }
                            }
                            failItem.classList.add('download-success');
                        }

                        return promiseFinally();
                    },
                    (xhr) => {
                        // 处理失败请求

                        // 寻找下载失败的文件项目
                        const path = root.struct[root.i]['path'];
                        let failItem;
                        const itemArr = root.querySelectorAll('.item');
                        for (let i = 0; i < itemArr.length; i++) {
                            if (itemArr[i].getAttribute('data-path') === path) {
                                failItem = itemArr[i];
                                break;
                            }
                        }

                        // 添加“×”
                        failItem.classList.add('download-fail');

                        // 将失败的文件项目添加到文件列表
                        const item = document.createElement('li');
                        item.classList.add('item');
                        item.classList.add('text-light');
                        item.classList.add('py-1');
                        item.textContent = path;
                        modal.querySelector('.fail-file-list .list').append(item);
                        showFailFileList();

                        return promiseFinally();
                    }
                );
            }

            // 导出zip
            promise.then((content) => {
                downloadFinishStatus();
                saveAs(content, MyFunction.splitPath(rootPath)[1] + '.zip');
            });
        });
        */

        // endregion

        function showLoading() {
            modal.querySelector('.loading').classList.remove('d-none');
        }

        function hiddenLoading() {
            modal.querySelector('.loading').classList.add('d-none');
        }

        function showStructFail(message) {
            modal.querySelector('.load-struct-fail .message').innerHTML = message;
            modal.querySelector('.load-struct-fail').classList.remove('d-none');
        }

        function hiddenStructFail() {
            modal.querySelector('.load-struct-fail').classList.add('d-none');
            modal.querySelector('.load-struct-fail .message').innerHTML = '';
        }

        function foldDir(e) {
            const item = e.target.parentNode;
            const fold = item.getAttribute('data-fold');
            if (fold === '1') {
                item.children[2].classList.remove('d-none');
                item.setAttribute('data-fold', '0');
            } else {
                item.children[2].classList.add('d-none');
                item.setAttribute('data-fold', '1');
            }
        }

        function foldAll() {
            root.querySelectorAll('.item').forEach((item) => {
                if (item.getAttribute('data-fold') === '0') {
                    item.querySelector('.filename').click();
                }
            });
        }

        function unfoldAll() {
            root.querySelectorAll('.item').forEach((item) => {
                if (item.getAttribute('data-fold') === '1') {
                    item.querySelector('.filename').click();
                }
            });
        }

        function addFileToStruct(fatherNode, path, type, filename, size) {
            const child = document.createElement('li');
            child.classList.add('item');
            child.classList.add('py-1');
            child.setAttribute('data-path', path);
            child.setAttribute('data-type', type);
            child.setAttribute('data-fold', '0');
            child.innerHTML = '<span class="filesize text-light"></span><span class="filename text-light"></span>';
            child.querySelector('.filename').textContent = filename;
            fatherNode.appendChild(child);
            if (type === 'dir') {
                const ul = document.createElement('ul');
                ul.classList.add('list');
                ul.setAttribute('data-path', path);
                child.appendChild(ul);
                child.querySelector('.filename').addEventListener('click', foldDir);
                return ul;
            }
            child.querySelector('.filesize').classList.add('me-2');
            child.querySelector('.filesize').textContent = '(' + size + ')';
            return null;
        }

        function buildStruct(struct) {
            root.setAttribute('data-path', struct[0]['path']);

            const fatherMap = {
                '.': root
            };
            for (let i = 1; i < struct.length; i++) {
                let path = struct[i]['path'];
                let type = struct[i]['type'];
                let size = struct[i]['size'];
                let [father, filename] = MyFunction.splitPath(path);

                let newFather = addFileToStruct(fatherMap[father], path, type, filename, size);
                if (newFather) {
                    fatherMap[path] = newFather;
                }
            }

            foldAll();
            root.classList.remove('d-none');
        }

        function clearStruct() {
            root.classList.add('d-none');
            root.innerHTML = '';
        }

    })();

    // 查看目录大小
    (() => {
        const modal = document.getElementById('dir-size-modal');

        document.querySelectorAll('#app .file-list .action-dropdown .dir-size').forEach((a) => {
            a.addEventListener('click', (e) => {
                // 初始化模态框
                modal.querySelector('.fail-info').classList.add('d-none');
                modal.querySelector('.dir-info').classList.add('d-none');
                modal.querySelector('.loading').classList.remove('d-none');
                modal.querySelector('.dir-info .name').textContent = a.getAttribute('data-file-name');
                (new bootstrap.Modal(modal, {keyboard: false})).show();

                // AJAX请求目录大小
                const url = a.getAttribute('data-href');
                MyAJAX.getJson(url).then(
                    (data) => {
                        modal.querySelector('.dir-info .size').textContent = data.result;
                        modal.querySelector('.loading').classList.add('d-none');
                        modal.querySelector('.dir-info').classList.remove('d-none');
                    },
                    (data) => {
                        modal.querySelector('.fail-info .message').textContent = data.message;
                        modal.querySelector('.loading').classList.add('d-none');
                        modal.querySelector('.fail-info').classList.remove('d-none');
                    }
                );
            });
        });
    })();

    // 下载目录时，弹出提示
    (() => {
        document.querySelectorAll('#app .file-list .action-dropdown .download-dir').forEach((a) => {
            a.addEventListener('click', (e) => {
                MyFunction.alert('提示', '目录将会被压缩，请等待...');
            });
        });
    })();

})(window, document);