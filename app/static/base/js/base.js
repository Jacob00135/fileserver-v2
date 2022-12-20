((window, document) => {
    'use strict';

    // 设置隐藏控件的值：当前url
    document.querySelectorAll('form input.current-url').forEach((input) => {
        input.setAttribute('value', location.pathname);
    });

    // 登出按钮
    (() => {
        const logoutLink = document.querySelector('#top-navbar .logout');
        if (!logoutLink) return undefined;
        logoutLink.addEventListener('click', () => {
            document.forms['logout'].submit();
        });
    })();

})(window, document);