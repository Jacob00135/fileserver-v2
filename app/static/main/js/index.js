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

})(window, document);