((window, document) => {
    // 事件委托：用户列表每一项的事件委托给父级
    document.querySelectorAll('#app .visible-dir-list').forEach((ul) => {
        ul.addEventListener('click', (e) => {
            // 检查事件源
            let index = e.target.getAttribute('data-event');
            if (index === null) return undefined;

            // 选中/取消选中一个项目
            index = parseInt(index);
            const li = ul.children[index];
            if (li.getAttribute('data-active') === '1') {
                li.setAttribute('data-active', '0');
            } else {
                li.setAttribute('data-active', '1');
            }
            const input = ul.children[index].querySelector('input[name="dir-path"][type="checkbox"]')
            if (e.target !== input) {
                input.checked = !input.checked;
            }
        });
    });

    // 全选按钮
    document.querySelectorAll('[id$="-all-select"]').forEach((btn) => {
       btn.addEventListener('click', () => {
           const userClasses = btn.id.replace('-all-select', '');
           document.querySelectorAll('#app #' + userClasses + ' .visible-dir-list > .list-group-item').forEach((item) => {
               if (item.getAttribute('data-active') === '0') {
                   item.click();
               }
           });
       });
    });

    // 全不选按钮
    document.querySelectorAll('[id$="-no-select"]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const userClasses = btn.id.replace('-no-select', '');
            document.querySelectorAll('#app #' + userClasses + ' .visible-dir-list > .list-group-item').forEach((item) => {
                if (item.getAttribute('data-active') === '1') {
                    item.click();
                }
            });
        });
    });

    // 反选按钮
    document.querySelectorAll('[id$="-anti-select"]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const userClasses = btn.id.replace('-anti-select', '');
            document.querySelectorAll('#app #' + userClasses + ' .visible-dir-list > .list-group-item').forEach((item) => {
                item.click();
            });
        });
    });

    // 添加可见目录表单
    (() => {
        const modal = document.getElementById('add-visible-dir-modal');
        const form = document.forms['add-visible-dir'];
        document.querySelectorAll('[id$="-add-visible-dir"]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                form.querySelector('input[name="permission"]').setAttribute('value', btn.getAttribute('data-permission'));
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 删除可见目录时，弹出提示模态框
    (() => {
        const modal = document.getElementById('delete-visible-dir-modal');
        const form = document.forms['delete-visible-dir'];
        document.querySelectorAll('#app .visible-dir-list .delete').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const dirPath = btn.getAttribute('data-dir-path');
                form.querySelector('.dir-path').innerHTML = dirPath;
                form.querySelector('input[name="dir-path"]').setAttribute('value', dirPath);
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 批量删除表单验证
    (() => {
        const modal = document.getElementById('delete-multi-visible-dir-modal');
        const form = document.forms['delete-multi-visible-dir'];
        const visibleDirList = form.querySelector('.visible-dir-list');
        document.querySelectorAll('[id$="-batch-delete"]').forEach((btn) => {
            const userClasses = btn.id.replace('-batch-delete', '');
            btn.addEventListener('click', (e) => {
                // 获取已选中的项目
                const checkedVisibleDir = [];
                document.querySelectorAll('#app #' + userClasses + ' .visible-dir-list input[name="dir-path"][type="checkbox"]').forEach((input) => {
                    if (input.checked) {
                        checkedVisibleDir.push(input.value);
                    }
                });
                if (checkedVisibleDir.length <= 0) return undefined;

                // 添加提示信息
                visibleDirList.innerHTML = '';
                checkedVisibleDir.forEach((visibleDir) => {
                    const hintInfo = document.createElement('span');
                    hintInfo.className = 'bg-danger bg-opacity-75 px-1 rounded-1 user-name';
                    hintInfo.innerHTML = visibleDir;
                    visibleDirList.appendChild(hintInfo);

                    visibleDirList.appendChild(document.createElement('br'));

                    const input = document.createElement('input');
                    input.className = 'd-none';
                    input.type = 'text';
                    input.name = 'dir-path';
                    input.setAttribute('value', visibleDir);
                    input.setAttribute('required', 'required');
                    visibleDirList.appendChild(input);
                });

                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();
})(window, document);
