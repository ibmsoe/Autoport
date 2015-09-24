
function createclusterfunc(){
    $.ajax({
        url: '/autoport/createAutoportStack',
        success:processResults,
        cache: false,
        contentType: false,
        processData: false
    }).fail(processResults);
}

function processResults(data) {
    if (data.status != "ok") {
        alert('Error: \n' + data.error);
    } else {
        alert('Successful: \n' + data.message);
    }
}
