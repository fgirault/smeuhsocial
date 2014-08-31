jQuery(document).ready(function($) {
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
      
      $('#new_tweet').keyup(function() {
          update_chars_left();
      });
      
      $("#touite_form").submit(function() {
  		var urlSubmit = $(this).attr('action');
  		$.ajax({  
  			type: "POST",
  			url: urlSubmit,
  			data: $(this).serializeArray(),
  			success: function(data) {
  				//alert(data);
  				$('#new_tweet')[0].value = "";
  				update_chars_left();
  				$("#timeline").prepend(data);
  			}
  		});
  		return false;
  	});
  	
    };
});