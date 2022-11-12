((window, document) => {
    'use strict';

    // 设置登录模态框的隐藏控件的值：当前url
    (() => {
        const currentUrlInput = document.getElementById('current-url');
        if (!currentUrlInput) return undefined;
        currentUrlInput.setAttribute('value', location.pathname);
    })();

    // 自动关闭登录失败时的警告框
    (() => {
        const loginFailAlertCloseBtn = document.querySelector('.login-fail-alert .btn-close');
        if (!loginFailAlertCloseBtn) return undefined;
        setTimeout(() => {
            loginFailAlertCloseBtn.click();
        }, 3000);
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