function humanizeBytes(value) {
    var bytes = parseInt(value)
    if(bytes > 1024*1024) {
        return Math.round((bytes / 1024) / 1024) + " MB";
    } else if (bytes > 1024) {
        return Math.round(bytes / 1024) + " KB";
    } else {
        return Math.round(bytes) + " bytes"
    }
}

function legend(parent, data) {
    parent.className = 'legend';
    var datas = data.hasOwnProperty('datasets') ? data.datasets : data;

    // remove possible children of the parent
    while(parent.hasChildNodes()) {
        parent.removeChild(parent.lastChild);
    }

    datas.forEach(function(d) {
        var title = document.createElement('li');
        title.className = 'label';
        title.style.backgroundColor = d.hasOwnProperty('strokeColor') ? d.strokeColor : d.color;
        parent.appendChild(title);

        var text = document.createTextNode(d.title + " - " + humanizeBytes(d.value));
        title.appendChild(text);
    });
}