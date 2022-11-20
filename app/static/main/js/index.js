((window, document) => {

    // 查看完整文件名
    (() => {
        const modal = document.getElementById('full-file-name-modal');
        const show = modal.querySelector('.show-file-name');
        const copyBtn = modal.querySelector('.copy-btn');
        const copyIcon = modal.querySelector('.copy-icon');

        // 弹出模态框
        document.querySelectorAll('#app .file-list .action-dropdown .full-file-name').forEach((a) => {
            a.addEventListener('click', (e) => {
                show.value = a.getAttribute('data-file-name');
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });

        // 复制按钮
        copyBtn.addEventListener('click', (e) => {
            show.select();
            document.execCommand('copy');
            copyIcon.classList.remove('bi-clipboard');
            copyIcon.classList.add('bi-check2');
            setTimeout(() => {
                copyIcon.classList.remove('bi-check2');
                copyIcon.classList.add('bi-clipboard');
            }, 2000);
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
        const copyBtn = form.querySelector('.copy-btn');
        const copyIcon = form.querySelector('.copy-icon');

        document.querySelectorAll('#app .file-list .action-dropdown .rename').forEach((a) => {
            a.addEventListener('click', (e) => {
                const filePath = a.getAttribute('data-file-path');
                const fileName = a.getAttribute('data-file-name');
                form.querySelector('input[name="path"]').setAttribute('value', filePath);
                form.querySelector('.source-file-name').setAttribute('value', fileName);
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
        copyBtn.addEventListener('click', (e) => {
            form.querySelector('.source-file-name').select();
            document.execCommand('copy');
            copyIcon.classList.remove('bi-clipboard');
            copyIcon.classList.add('bi-check2');
            setTimeout(() => {
                copyIcon.classList.remove('bi-check2');
                copyIcon.classList.add('bi-clipboard');
            }, 2000);
        });
    })();

})(window, document);