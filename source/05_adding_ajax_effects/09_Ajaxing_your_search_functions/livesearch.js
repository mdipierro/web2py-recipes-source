function livesearch(value){
    if(value != ""){
        jQuery("#livesearchresults").show();
        jQuery.post(livesearch_url,
                    {keywords:value},
                    function(result){
                        jQuery("#livesearchresults").html(result);
                    }
        );
    }
    else {
        jQuery("#livesearchresults").hide();
    }
}
function updatelivesearch(value){
    jQuery("#livesearch").val(value);jQuery("#livesearchresults").hide();
}
jQuery(function(){jQuery("#livesearchresults").hide();});
