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
            const input = ul.children[index].querySelector('input[name="user-name"]')
            input.checked = !input.checked;
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
})(window, document);
