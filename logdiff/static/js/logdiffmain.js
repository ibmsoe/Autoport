google.load('search', '1');

$('#file1').change(function () {
    var empty = true;
    if ($('#file1').val().length > 0 && $('#file2').val().length > 0) {
        empty = false;
    }
    if (empty) {
        $("#filecompbtn").prop("disabled", true);
    } else {
        $("#filecompbtn").prop("disabled", false);
    }
});

$('#file2').change(function () {
    var empty = true;
    if ($('#file1').val().length > 0 && $('#file2').val().length > 0) {
        empty = false;
    }
    if (empty) {
        $("#filecompbtn").prop("disabled", true);
    } else {
        $("#filecompbtn").prop("disabled", false);
    }
});

$('#text1').on("change keyup paste", function () {
    var empty = true;
    if ($('#text1').val().length > 0 && $('#text2').val().length > 0) {
        empty = false;
    }
    if (empty) {
        $("#textcompbtn").prop("disabled", true);
    } else {
        $("#textcompbtn").prop("disabled", false);
    }
});

$('#text2').on("change keyup paste", function () {
    var empty = true;
    if ($('#text1').val().length > 0 && $('#text2').val().length > 0) {
        empty = false;
    }
    if (empty) {
        $("#textcompbtn").prop("disabled", true);
    } else {
        $("#textcompbtn").prop("disabled", false);
    }
});

function filecompfunc(){
    var file1 = $("#file1")[0].files[0];
    var fileName1 = file1.name;

    var file2 = $("#file2")[0].files[0];
    var fileName2 = file2.name;

    if ($('#file1').val().length > 0 && $('#file2').val().length > 0) {
        var formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);

        $.ajax({
         url: "/getFileDiffResults",
         type: 'POST',
         data: formData,
                async: true,
        success: processCompareResults,
                cache: false,
        contentType: false,
                processData: false
         }).fail(processCompareResults);
    } else {
        $('#resultCompareSelectionAlert').modal();
    }
}

function textcompfunc(){
    var text1 = $("#text1").val();
    var text2 = $("#text2").val();

    if ($('#text1').val().length > 0 && $('#text2').val().length > 0) {
        var formData = new FormData();
        formData.append('text1', text1);
        formData.append('text2', text2);

        $.ajax({
         url: "/getTextDiffResults",
         type: 'POST',
         data: formData,
                async: true,
        success: processCompareResults,
                cache: false,
        contentType: false,
                processData: false
         }).fail(processCompareResults);
    } else {
        $('#resultCompareSelectionAlert').modal();
    }
}

function processCompareResults(data) {
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        $("#leftdiff").html(data.leftcontent);
        $("#rightdiff").html(data.rightcontent);
        $("#logdiffHeader").html("for " + data.leftname + " / " + data.rightname);
        $('#logdiffModal').on('show.bs.modal', function() {
            $('#leftdiff span, #rightdiff span').each(function(index) {
                var elementID = "searchcontrol"+index;
				var html = '<div id="' + elementID + '"></div>';
				$('#logdiffModal').append(html);
				$(this).qtip({
					content: {
						text: function(event, api) {
							var searchControl = new google.search.SearchControl();
							searchControl.addSearcher(new google.search.WebSearch());
							searchControl.draw(document.getElementById(elementID));
							var searchword = $(this).text();
							if (searchword.length>40) {
								searchword = searchword.substring(searchword.length-40);
							}
							searchControl.execute(searchword);
							return $("#"+elementID);
						},
						title: 'From Google Search',
						button: true
					},
					position: {
						viewport: $(window)
					},
					hide: false
				});
			});
		});
        $('#logdiffModal').on('hidden.bs.modal', function () {
            $('#leftdiff span, #rightdiff span').each(function(index) {
				if( $(this).data('qtip')) {
					$(this).qtip('destroy', true);
				}
		    });
		});
        $('#logdiffModal').modal('show');
    }
}

function showAlert(message, data) {
    var text = message;
    if (typeof data !== "undefined") {
        text += "<br/>" + (data.responseJSON !== undefined ?
                            (data.responseJSON.error !== undefined ?
                              data.responseJSON.error :
                              data.error) :
                            data.error);
    }
    $("#apErrorDialogText").html(text);
    $("#errorAlert").modal();
}