let ho = {
    entityMap: {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
    },

    escape: function (str) {
        return String(str).replace(/[&<>"'`=\/]/g, function (c) {
            return ho.entityMap[c];
        });
    },
};