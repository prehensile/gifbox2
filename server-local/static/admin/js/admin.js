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

    console.log( state );

    /*
    $.post(
        "/api/admin/state",
        state,
        function(data){
            console.log( data );
        }
    )*/

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