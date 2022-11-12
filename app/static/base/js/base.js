((window, document) => {
    'use strict';

    // 设置隐藏控件的值：当前url
    document.querySelectorAll('form input.current-url').forEach((input) => {
        input.setAttribute('value', location.pathname);
    });

    // 自动关闭警告框
    (() => {
        let clickDelayTime = 3000;
        document.querySelectorAll('#app .top-alert .btn-close').forEach((closeBtn) => {
            setTimeout(() => {
                closeBtn.click();
            }, clickDelayTime);
            clickDelayTime = clickDelayTime + 3000;
        });
    })();

    // 登出按钮
    (() => {
        const logoutLink = document.querySelector('#navbar-menu .logout');
        if (!logoutLink) return undefined;
        logoutLink.addEventListener('click', () => {
            document.forms['logout'].submit();
        });
    })();

})(window, document);