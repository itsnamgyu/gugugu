$("#form-content").keydown(function(e){
    if (e.keyCode === 13 && !e.shiftKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        $("#form-submit").click()
        return false;
    }
});
