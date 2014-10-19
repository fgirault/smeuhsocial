/*
 * Some basic javascript to perform validation 
 */
jQuery(document).ready(function($) {
	
	$("#touite_form").submit(function(e) {    	
    	e.preventDefault();
  		var urlSubmit = $(this).attr('action');
  		var data = $(this).serializeArray();
  		$("#touite_form :input").prop("disabled", true);
  		$.ajax({  
  			type: "POST",
  			url: urlSubmit,
  			data: data,
  			success: function(data) {
  				$('#new_tweet')[0].value = "";
  				//update_chars_left();
  				$('#new_tweet').blur();
  				
  				var div = $(data).hide();
  				$("#timeline div:first-child").first().prepend(div);
  			    div.slideDown("slow");
  			    $("#touite_form :input").prop("disabled", false);
  			    $('#touite_bang').prop("disabled", true);
  			},
  			error: function(data) {
  				// TODO integrate error report in ui
  				alert("Error posting touite");
  				$("#touite_form :input").prop("disabled", false);
  			}
  		});  		
  	});
	
	$('#touite_bang').prop("disabled", true);
	
	$('#new_tweet').keyup(function() {
		// prevent submit button to be clicked if text is not ok
		var textarea = $('#new_tweet')[0];
        if(textarea.value.length > 0 && textarea.value.length < 140) {
        	$("#touite_bang").prop("disabled", false);
        } else {
        	$('#touite_bang').prop("disabled", true);
        }
        
    });
	
	
	/*
    if ($('#new_tweet').length) {
      function update_chars_left() {
    	  $('#new_tweet').popover('show');
          var max_len = 140;
          var textarea = $('#new_tweet')[0];
          var tweet_len = textarea.value.length;
          if (tweet_len >= max_len) {
              textarea.value = textarea.value.substring(0, max_len); // truncate
              $('#chars_left').html("0");
          } else {
        	  $('#chars_left').html(max_len - tweet_len);
          }
      }
      /*
      $('#new_tweet').keyup(function() {
          update_chars_left();
      });
    };
	 */
      
      
  	
});