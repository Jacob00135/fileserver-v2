((window, document) => {

    (() => {
        const app = document.getElementById('app');
        app.classList.remove('container');
        app.classList.add('container-fluid');
    })();

})(window, document);