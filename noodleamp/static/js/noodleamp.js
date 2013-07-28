;(function($) {
    var $document = $(document);
    var $play = $('.play');
    var $length = $('.status .length');
    var $progress = $('.status .songprogress');
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
            $nowPlaying.text(data['current_song']);
            $progress.text(data['progress']);
            $length.text(data['length']);
        });
    }
    setInterval(getstatus, 1000);

    var paused = false;
    function play(file) {
        $play.find('.text').text('Pause');
        $play.find('.icon').attr('class', 'icon icon-pause');
        $nowPlaying.text(file);
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
