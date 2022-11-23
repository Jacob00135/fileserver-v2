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
            xhr.addEventListener('readystatechange', () => {
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

})(window, document);