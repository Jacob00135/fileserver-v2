window.MyFunction = {
    inArray: (array, value) => {
        for (let i = 0; i < array.length; i++) {
            if (array[i] === value) {
                return true;
            }
        }
        return false;
    },

    alert: (title = '警告', message = '') => {
        const modal = document.getElementById('hint-modal');
        modal.querySelector('.modal-title').innerHTML = title;
        modal.querySelector('.modal-body').innerHTML = message;
        (new bootstrap.Modal(modal, {keyboard: false})).show();
    },

    copy: (text, father) => {
        const input = document.createElement('input');
        input.value = text;
        father.appendChild(input);
        input.select();
        document.execCommand('copy');
        father.removeChild(input);
    }
};