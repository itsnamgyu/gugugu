var granimInstance = new Granim({
    element: '#canvas-background',
    direction: 'left-right',
    isPausedWhenNotInView: true,
    states : {
        "default-state": {
            gradients: [["#501145", "#C63771"], ["#FD804A", "#A70F2B"]]
        }
    }
});

$("#form-content").keydown(function(e){
    if (e.keyCode === 13 && !e.shiftKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        $("#form-submit").click()
        return false;
    }
});
