const setupPngFileCollapse = function(){
    const clpsPngFile = $('#clpsPngFile');
    $("input[name='rdoOverlay']").change(function(){
        if ($(this).val() == 'png') {
            clpsPngFile.collapse('show');
        } else {
            clpsPngFile.collapse('hide');
        }
    });
}


const sendFormState = function(){
    
    let state = { "test" : true };

    const fields = $('#frmConfig').serializeArray();
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        state[ field['name'] ] = field['value'];
    }

    // upload png file, if necessary
    let overlayVal = $("input[name=rdoOverlay]:checked").val();
    if( overlayVal == "png" ){

        // cribbed from https://stackoverflow.com/questions/2320069/jquery-ajax-file-upload
        var formData = new FormData();
        formData.append('file', $('#fileOverlay')[0].files[0]);

        $.ajax({
            url : '/admin/files/upload',
            type : 'POST',
            data : formData,
            processData: false,  // tell jQuery not to process the data
            contentType: false,  // tell jQuery not to set contentType
            success : function(data) {
                console.log(data);
            }
        });
    }

    // send form state
    $.ajax({
        url: "/api/admin/state",
        method: 'POST',
        contentType: "application/json",
        data: JSON.stringify( state ),
        success: function(data){
            console.log( data );
        }
    });
}


$( document ).ready(function() {
    
    setupPngFileCollapse();

    // send form state when button is pressed
    $('#btnSubmit').click(function(e){
        e.preventDefault();
        sendFormState();
    });

});