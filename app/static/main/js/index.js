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
        if (!modal) return undefined;
        const form = document.forms['delete-file'];

        document.querySelectorAll('#app .file-list .action-dropdown .remove').forEach((a) => {
            a.addEventListener('click', (e) => {
                form.querySelector('.file-name').textContent = a.getAttribute('data-file-name');
                form.querySelector('input[name="path"]').setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 重命名文件
    (() => {
        const modal = document.getElementById('rename-file-modal');
        if (!modal) return undefined;
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

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 移动文件
    (() => {
        const modal = document.getElementById('move-file-modal');
        if (!modal) return undefined;
        const form = document.forms['move-file'];
        const filePathInput = form.querySelector('input[name="source-file-path"]');

        document.querySelectorAll('#app .file-list .action-dropdown .move').forEach((a) => {
            a.addEventListener('click', (e) => {
                filePathInput.setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 复制文件
    (() => {
        const modal = document.getElementById('copy-file-modal');
        if (!modal) return undefined;
        const form = document.forms['copy-file'];
        const filePathInput = form.querySelector('input[name="source-file-path"]');

        document.querySelectorAll('#app .file-list .action-dropdown .copy').forEach((a) => {
            a.addEventListener('click', (e) => {
                filePathInput.setAttribute('value', a.getAttribute('data-file-path'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 上传文件
    (() => {
        const form = document.forms['upload-file'];
        if (!form) return undefined;
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
        if (!modal) return undefined;

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
                        modal.querySelector('.dir-info .size').textContent = data.result.total;
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

    // 多选按钮
    (() => {
        const btn = document.getElementById('multi-select');
        if (!btn) return undefined;
        const topNode = document.querySelector('#app .file-list');
        const fileList = document.querySelectorAll('#app .file-list .list-group-item:not(.upper-path)');
        const hrefArr = [];

        // 多选按钮点击事件
        btn.addEventListener('click', (e) => {
            if (btn.getAttribute('data-multi-status') === '0') {
                btn.setAttribute('data-multi-status', '1');
                startMultiSelect();
            } else {
                btn.setAttribute('data-multi-status', '0');
                quitMultiSelect();
            }
        });

        // 勾选多选框事件
        fileList.forEach((item) => {
            const index = item.getAttribute('data-index');
            const input = item.querySelector('.multi-select');
            input.addEventListener('change', (e) => {
                if (input.checked) {
                    item.setAttribute('data-active', '1');

                    // 设置区间选择的起始和结束下标
                    if (topNode.getAttribute('data-select-start-index') === '-1') {
                        topNode.setAttribute('data-select-start-index', index);
                    } else if (topNode.getAttribute('data-select-end-index') === '-1') {
                        topNode.setAttribute('data-select-end-index', index);
                    } else {
                        topNode.setAttribute('data-select-start-index', topNode.getAttribute('data-select-end-index'));
                        topNode.setAttribute('data-select-end-index', index);
                    }
                } else {
                    item.setAttribute('data-active', '0');
                    topNode.setAttribute('data-select-start-index', '-1');
                    topNode.setAttribute('data-select-end-index', '-1');
                }
            });
        });

        function startMultiSelect() {
            // 进入多选状态
            document.querySelector('#app .file-list').setAttribute('data-multi-select-status', '1');
            document.querySelector('#app .secondary-multi-select-btn-group').classList.remove('d-none');

            // 重置区间选择的起始、结束下标
            topNode.setAttribute('data-select-start-index', '-1');
            topNode.setAttribute('data-select-end-index', '-1');

            // 操作列表项
            fileList.forEach((item) => {
                const input = item.querySelector('.multi-select');
                const a = item.querySelector('.file-name');

                // 移除所有文件链接，同时把链接暂时保存到数组
                hrefArr.push(a.getAttribute('href'));
                a.removeAttribute('href');

                // 显示所有的多选框
                input.classList.remove('d-none');

                // 取消选择
                if (input.checked) {
                    input.click();
                }

                // 为文件链接添加复选框点击事件
                a.selectEvent = (e) => {
                    input.click();
                };
                a.addEventListener('click', a.selectEvent);
            });

            // 显示多选操作下拉按钮
            document.getElementById('multi-select-dropdown-btn').classList.remove('d-none');
        }

        function quitMultiSelect() {
            // 隐藏多选操作下拉按钮
            document.getElementById('multi-select-dropdown-btn').classList.add('d-none');

            // 退出多选状态
            document.querySelector('#app .file-list').setAttribute('data-multi-select-status', '0');
            document.querySelector('#app .secondary-multi-select-btn-group').classList.add('d-none');

            // 操作列表项
            fileList.forEach((item) => {
                const input = item.querySelector('.multi-select');
                const a = item.querySelector('.file-name');

                // 取消选择
                if (input.checked) {
                    input.click();
                }

                // 隐藏所有多选框
                input.classList.add('d-none');

                // 添加文件链接
                a.setAttribute('href', hrefArr.shift());

                // 移除文件链接的复选框点击事件
                a.removeEventListener('click', a.selectEvent);
            });
        }

    })();

    // 多选辅助：全选、全不选、反选、区间选择
    (() => {
        const topNode = document.querySelector('#app .file-list');
        const fileList = document.querySelectorAll('#app .file-list .list-group-item:not(.upper-path)');
        const allSelectBtn = document.querySelector('.secondary-multi-select-btn-group .all-select');
        const noSelectBtn = document.querySelector('.secondary-multi-select-btn-group .no-select');
        const antiSelectBtn = document.querySelector('.secondary-multi-select-btn-group .anti-select');
        const betweenSelectBtn = document.querySelector('.secondary-multi-select-btn-group .between-select');

        if (allSelectBtn) {
            allSelectBtn.addEventListener('click', (e) => {
                fileList.forEach((item) => {
                    if (item.getAttribute('data-active') !== '1') {
                        item.querySelector('input[name="file-name"]').click();
                    }
                });
                topNode.setAttribute('data-select-start-index', '-1');
                topNode.setAttribute('data-select-end-index', '-1');
            });
        }

        if (noSelectBtn) {
            noSelectBtn.addEventListener('click', (e) => {
                fileList.forEach((item) => {
                    if (item.getAttribute('data-active') === '1') {
                        item.querySelector('input[name="file-name"]').click();
                    }
                });
                topNode.setAttribute('data-select-start-index', '-1');
                topNode.setAttribute('data-select-end-index', '-1');
            });
        }

        if (antiSelectBtn) {
            antiSelectBtn.addEventListener('click', (e) => {
                fileList.forEach((item) => {
                    item.querySelector('input[name="file-name"]').click();
                });
                topNode.setAttribute('data-select-start-index', '-1');
                topNode.setAttribute('data-select-end-index', '-1');
            });
        }

        if (betweenSelectBtn) {
            betweenSelectBtn.addEventListener('click', (e) => {
                let start = parseInt(topNode.getAttribute('data-select-start-index'));
                let end = parseInt(topNode.getAttribute('data-select-end-index'));
                if (start === -1 || end === -1) return undefined;

                if (start > end) {
                    const t = start;
                    start = end;
                    end = t;
                }

                for (let i = start + 1; i < end; i++) {
                    if (fileList[i].getAttribute('data-active') !== '1') {
                        fileList[i].querySelector('.file-name').click();
                    }
                }

                topNode.setAttribute('data-select-start-index', '-1');
                topNode.setAttribute('data-select-end-index', '-1');
            });
        }
    })();

    // 多选删除
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .remove');
        if (!btn) return undefined;
        const modal = document.getElementById('delete-multi-file-modal');
        const form = document.forms['delete-multi-file'];

        btn.addEventListener('click', (e) => {
            // 收集要删除的文件的路径
            const htmlList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
                .forEach((input) => {
                    const html = `<span class="bg-danger bg-opacity-75 px-1 rounded-1">{{ file-name }}</span>
                    <br/>
                    <input class="d-none" type="text" name="path" value="{{ file-path }}" required="required"/>`
                        .replace('{{ file-path }}', input.value)
                        .replace('{{ file-name }}', input.value.split('\\').pop());
                    htmlList.push(html);
                });
            if (htmlList.length <= 0) return undefined;

            // 显示模态框
            modal.querySelector('.file-path-list').innerHTML = htmlList.join('');
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 多选移动
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .move');
        if (!btn) return undefined;
        const modal = document.getElementById('move-multi-file-modal');
        const form = document.forms['move-multi-file'];

        btn.addEventListener('click', (e) => {
            // 收集要移动的文件的路径
            const htmlList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
                .forEach((input) => {
                    const html = `<span class="bg-info bg-opacity-75 px-1 rounded-1">{{ file-name }}</span>
                    <br/>
                    <input class="d-none" type="text" name="source-file-path" value="{{ file-path }}"
                        required="required"/>`
                        .replace('{{ file-path }}', input.value)
                        .replace('{{ file-name }}', input.value.split('\\').pop());
                    htmlList.push(html);
                });
            if (htmlList.length <= 0) return undefined;

            // 显示模态框
            modal.querySelector('.file-path-list').innerHTML = htmlList.join('');
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 多选复制
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .copy');
        if (!btn) return undefined;
        const modal = document.getElementById('copy-multi-file-modal');
        const form = document.forms['copy-multi-file'];

        btn.addEventListener('click', (e) => {
            // 收集要复制的文件的路径
            const htmlList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
                .forEach((input) => {
                    const html = `<span class="bg-info bg-opacity-75 px-1 rounded-1">{{ file-name }}</span>
                    <br/>
                    <input class="d-none" type="text" name="source-file-path" value="{{ file-path }}"
                        required="required"/>`
                        .replace('{{ file-path }}', input.value)
                        .replace('{{ file-name }}', input.value.split('\\').pop());
                    htmlList.push(html);
                });
            if (htmlList.length <= 0) return undefined;

            // 显示模态框
            modal.querySelector('.file-path-list').innerHTML = htmlList.join('');
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });

        form.addEventListener('submit', (e) => {
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 多选文件查看总大小
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .total-size');
        if (!btn) return undefined;
        const modal = document.getElementById('multi-total-size-modal');

        btn.addEventListener('click', (e) => {
            // 收集文件路径信息
            const fpList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
            .forEach((input) => {
                fpList.push(encodeURIComponent(input.value));
            });
            if (fpList.length <= 0) return undefined;

            // 初始化模态框
            modal.querySelector('.file-size-table').classList.add('d-none');
            modal.querySelector('.file-size-table .table tbody').innerHTML = '';
            modal.querySelector('.fail-info').classList.add('d-none');
            modal.querySelector('.loading').classList.remove('d-none');
            (new bootstrap.Modal(modal, {keyboard: false})).show();

            // ajax请求大小
            const url = btn.getAttribute('data-href') + '?path=' + fpList.join('&path=');
            MyAJAX.getJson(url).then(
                (data) => {
                    modal.querySelector('.loading').classList.add('d-none');
                    // 将data.result渲染到表格中
                    const tbody = modal.querySelector('.file-size-table .table tbody');
                    const trList = [];
                    data.result['size_list'].forEach((item) => {
                        const html = `<tr data-dir="{{ is_dir }}">
                            <td>{{ file_name }}</td>
                            <td>{{ file_size }}</td>
                        </tr>`
                            .replace('{{ is_dir }}', item['is_dir'])
                            .replace('{{ file_name }}', item['file_name'])
                            .replace('{{ file_size }}', item['file_size']);
                        trList.push(html);
                    });
                    tbody.innerHTML = `<tr class="total"><td>总计</td><td></td></tr>` + trList.join('');
                    tbody.querySelector('.total > td:nth-child(2)').innerHTML = data.result.total;
                    modal.querySelector('.file-size-table').classList.remove('d-none');
                },
                (data) => {
                    modal.querySelector('.fail-info .message').innerHTML = data.message;
                    modal.querySelector('.loading').classList.add('d-none');
                    modal.querySelector('.fail-info').classList.remove('d-none');
                }
            );
        });
    })();

    // 压缩文件
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .compress-file');
        if (!btn) return undefined;
        const modal = document.getElementById('compress-file-modal');
        const form = document.forms['compress-file'];

        btn.addEventListener('click', (e) => {
            // 收集选择的文件信息
            const htmlList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
                .forEach((input) => {
                    const html = `<span class="bg-info bg-opacity-75 px-1 rounded-1">{{ file-name }}</span>
                        <br/>
                        <input class="d-none" type="text" name="file-path" value="{{ file-path }}"
                            required="required"/>`
                        .replace('{{ file-path }}', input.value)
                        .replace('{{ file-name }}', input.value.split('\\').pop());
                    htmlList.push(html);
                });
            if (htmlList.length <= 0) return undefined;

            // 显示模态框
            form.querySelector('.file-name-list .list').innerHTML = htmlList.join('');
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });

        form.addEventListener('submit', (e) => {
            modal.querySelector('.loading').classList.remove('d-none');
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 多选下载
    (() => {
        const btn = document.querySelector('#app .multi-select-btn-group .download');
        if (!btn) return undefined;
        const modal = document.getElementById('multi-download-modal');
        const form = document.forms['multi-download'];

        btn.addEventListener('click', (e) => {
            // 收集选择的文件信息
            const htmlList = [];
            document.querySelectorAll('#app .file-list .list-group-item[data-active="1"] input[name="file-name"]')
                .forEach((input) => {
                    const html = `<span class="bg-info bg-opacity-75 px-1 rounded-1">{{ file-name }}</span>
                        <br/>
                        <input class="d-none" type="text" name="path" value="{{ file-path }}"
                            required="required"/>`
                        .replace('{{ file-path }}', input.value)
                        .replace('{{ file-name }}', input.value.split('\\').pop());
                    htmlList.push(html);
                });
            if (htmlList.length <= 0) return undefined;

            // 显示模态框
            form.querySelector('.file-name-list .list').innerHTML = htmlList.join('');
            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });

        form.addEventListener('submit', (e) => {
            modal.querySelector('.loading').classList.remove('d-none');
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
        });
    })();

    // 分页导航的跳转按钮（省略号）
    (() => {
        const modal = document.getElementById('jump-page-modal');
        if (!modal) return undefined;
        document.querySelectorAll('#file-pagination .page-item.ellipsis').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 搜索按钮
    (() => {
        const modal = document.getElementById('search-modal');
        if (!modal) return undefined;
        const form = document.forms['search-file'];

        document.querySelectorAll('#top-navbar .search-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                modal.querySelector('.loading').classList.add('d-none');
                modal.querySelector('.search-result').classList.add('d-none');
                modal.querySelector('.no-result').classList.add('d-none');
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            form.querySelector('[type="submit"]').setAttribute('disabled', '');
            modal.querySelector('.no-result').classList.add('d-none');
            modal.querySelector('.search-result').classList.add('d-none');
            modal.querySelector('.loading').classList.remove('d-none');

            // ajax请求、渲染
            const dirPath = form.querySelector('input[name="dir-path"]').value;
            const keyword = form.querySelector('input[name="keyword"]').value;
            const url = form.action + '?dir-path=' + dirPath + '&keyword=' + keyword;
            MyAJAX.getJson(url).then(
                (data) => {
                    const htmlList = [];
                    data.result.forEach((item) => {
                        const html = `<li class="list-group-item bg-secondary p-0 border-dark">
                            <a class="text-decoration-none text-light flex-fill px-3 py-2 d-flex flex-column link"
                               href="{{ file_link }}" title="{{ file_path }}">
                                <div class="d-flex file-name">
                                    <i class="{{ file_icon }} me-1 align-self-center fs-5"
                                       data-file-type="{{ file_type }}"></i>
                                    <span class="fs-5 text-truncate flex-fill text">{{ filename }}</span>
                                </div>
                                <div class="text-truncate file-path">{{ file_path }}</div>
                            </a>
                        </li>`
                            .replace('{{ file_link }}', item['file_link'])
                            .replace('{{ file_icon }}', globalVariable.fileTypeIconMap[item['file_type']])
                            .replace('{{ file_type }}', item['file_type'])
                            .replace('{{ filename }}', item['filename'])
                            .replace(/\{\{ file_path \}\}/g, item['file_path'])
                        htmlList.push(html);
                    });

                    modal.querySelector('.search-result .list').innerHTML = htmlList.join('');
                    modal.querySelector('.search-result').classList.remove('d-none');
                    modal.querySelector('.loading').classList.add('d-none');
                    form.querySelector('[type="submit"]').removeAttribute('disabled');
                },
                (data) => {
                    modal.querySelector('.no-result').classList.remove('d-none');
                    modal.querySelector('.loading').classList.add('d-none');
                    form.querySelector('[type="submit"]').removeAttribute('disabled');
                }
            );
        });
    })();

})(window, document);