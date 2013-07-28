;(function($) {
    var $document = $(document);
    var $play = $('.play');
    var $length = $('.status .length');
    var $position = $('.status .position');
    var $nowPlaying = $('.now-playing .title');

    $(function() {
        $('.file-list').fileTree({
            script: '/library/',
            root: ''
        }, function(file) {
            $play.removeClass('disabled');
            play(file);
        });

        $document.on('click', '.play:not(.disabled)', function(e) {
            e.preventDefault();
            pause();
        });
    });

    function getstatus() {
        $.getJSON('/status/', function(data) {
            if (data['playing']) {
                $nowPlaying.text(data['artist'] + " - " + data['title'] );
                $position.text(data['position']);
                $length.text(data['length']);
            } else {
                $length.text('00:00');
                $position.text('00:00');
                $nowPlaying.text('');
            }
        });
    }
    setInterval(getstatus, 1000);

    var paused = false;
    function play(file) {
        $play.find('.text').text('Pause');
        $play.find('.icon').attr('class', 'icon icon-pause');
        paused = false;
        $.post('/play/', {path: file});
    }

    function pause() {
        if (paused) {
            $play.find('.text').text('Pause');
            $play.find('.icon').attr('class', 'icon icon-pause');
            paused = false;
        } else {
            $play.find('.text').text('Play');
            $play.find('.icon').attr('class', 'icon icon-play');
            paused = true;
        }

        $.post('/pause/');
    }
})(jQuery);
