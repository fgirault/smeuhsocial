$(document).ready(function() {

  function playNext(domObj) {
    var next_audio_elem = $(domObj).parents('.audiotracks-list-entry').next().find('audio').get(0);
    if (next_audio_elem) {
      var player = next_audio_elem.player;
      // FIXME
      // Only way to make play() work on Firefox is to wrap it in a
      // setTimeout. Weird...
      setTimeout($.proxy(player, 'play'), 0);
    } else {
      var pagination = $('.pagination');
      var current = pagination.find('.active');
      var next = current.next();
      if (next.size()) {
        var url = next.find('a').attr('href');
        window.location = url + '?autoplay=true';
      }
    }
  }

  $('audio').mediaelementplayer({
    audioWidth: 380, 
    success: function(me, domObj) {
      var container = $(domObj).parents('.player-container');
      container.next().find('.audio-type').html( me.pluginType );
      $(me).bind('ended', function() { playNext(domObj); });
      var firstPlayer = mejs.players[0];
      if (me === firstPlayer.media && location.search.indexOf('autoplay=true') != -1) {
        firstPlayer.play();
      }
    }
  });


});
