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

$( document ).ready(function() {
    
    setupPngFileCollapse();

});