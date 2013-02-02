;(function($) {
    var $document = $(document);
    var $play = $('.play');
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
