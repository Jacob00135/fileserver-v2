((window, document) => {
    // 事件委托：用户列表每一项的事件委托给父级
    (() => {
        const ul = document.querySelector('#app .user-list');
        ul.addEventListener('click', (e) => {
            // 检查事件源
            let index = e.target.getAttribute('data-event');
            if (index === null) return undefined;

            // 选中/取消选中一个用户
            index = parseInt(index);
            const li = ul.children[index];
            if (li.getAttribute('data-active') === '1') {
                li.setAttribute('data-active', '0');
            } else {
                li.setAttribute('data-active', '1');
            }
            const input = ul.children[index].querySelector('input[name="user-name"][type="checkbox"]')
            if (e.target !== input) {
                input.checked = !input.checked;
            }
        });
    })();

    // 全选按钮
    (() => {
        const allSelect = document.getElementById('all-select');
        allSelect.addEventListener('click', () => {
            document.querySelectorAll('#app .user-list > .list-group-item').forEach((item) => {
                if (item.getAttribute('data-active') === '0') {
                    item.click();
                }
            });
        });
    })();

    // 全不选按钮
    (() => {
        const noSelect = document.getElementById('no-select');
        noSelect.addEventListener('click', () => {
            document.querySelectorAll('#app .user-list > .list-group-item').forEach((item) => {
                if (item.getAttribute('data-active') === '1') {
                    item.click();
                }
            });
        });
    })();

    // 反选按钮
    (() => {
        const antiSelect = document.getElementById('anti-select');
        antiSelect.addEventListener('click', (item) => {
            document.querySelectorAll('#app .user-list > .list-group-item').forEach((item) => {
                item.click();
            });
        });
    })();

    // 删除用户时，弹出提示模态框
    (() => {
        const modal = document.getElementById('delete-user-modal');
        const form = document.forms['delete-user'];
        document.querySelectorAll('#app .user-list .delete').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const userName = btn.getAttribute('data-user-name');
                form.querySelector('.user-name').innerHTML = userName;
                form.querySelector('input[name="user-name"]').setAttribute('value', userName);
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();

    // 批量删除表单验证
    (() => {
        const modal = document.getElementById('delete-multi-user-modal');
        const form = document.forms['delete-multi-user'];
        const userNameList = form.querySelector('.user-name-list');
        document.getElementById('batch-delete').addEventListener('click', (e) => {
            // 获取已选中的用户名
            const checkedUserName = [];
            document.querySelectorAll('#app .user-list input[name="user-name"][type="checkbox"]').forEach((input) => {
                if (input.checked) {
                    checkedUserName.push(input.value);
                }
            });
            if (checkedUserName.length <= 0) return undefined;

            // 添加提示信息
            userNameList.innerHTML = '';
            checkedUserName.forEach((userName) => {
                const hintInfo = document.createElement('span');
                hintInfo.className = 'bg-danger bg-opacity-75 px-1 rounded-1 user-name';
                hintInfo.innerHTML = userName;
                userNameList.appendChild(hintInfo);

                userNameList.appendChild(document.createElement('br'));

                const input = document.createElement('input');
                input.className = 'd-none';
                input.type = 'text';
                input.name = 'user-name';
                input.setAttribute('value', userName);
                input.setAttribute('required', 'required');
                userNameList.appendChild(input);
            });

            (new bootstrap.Modal(modal, {keyboard: false})).show();
        });
        // form.addEventListener('submit', (e) => {
        //     e.preventDefault();
        //
        //     const userNameArr = form.querySelectorAll('input[name="user-name"]');
        //
        //     for (let i = 0; i < userNameArr.length; i++) {
        //         if (userNameArr[i].checked) {
        //             form.submit();
        //             return undefined;
        //         }
        //     }
        // });
    })();

    // 修改用户的密码
    (() => {
        const modal = document.getElementById('update-user-password-modal');
        const form = document.forms['update-user-password'];
        document.querySelectorAll('#app .user-list .update-password').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const userName = btn.getAttribute('data-user-name');
                form.querySelector('input[name="user-name"]').setAttribute('value', userName);
                (new bootstrap.Modal(modal, {keyboard: false})).show();
            });
        });
    })();
})(window, document);
