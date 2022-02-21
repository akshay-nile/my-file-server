$(document).ready(function() {

    // Hidding settings and search pannels

    $('.settings-pannel, .search-pannel').hide();


    // If it's a desktop screen then set body's CSS, then show body

    if (screen.width > screen.height)
        $('body').css({ 'width': '400px', 'margin': '0px auto', 'overflow': 'scroll' });

    $('body').show();


    // This function is to be called once all the items are loaded on the body

    function activateBodyItems(refreshThumbnails = true) {

        // Removing extra .item-gap hr from folder and file pannels added by jinja2 templates

        $('#folder-pannel .item-gap:last-child, #file-pannel .item-gap:last-child').remove();


        // Assigning click events to various td tags of file and folder pannels

        $('.folder-name, .folder-open, .file-download').click(function() {
            window.location.href = '/storage?path=' + $(this).parent().attr('path');
        });

        $('.folder-icon').click(function() {
            window.open('/storage?path=' + $(this).parent().attr('path'), '_blank');
        });

        $('.file-icon').click(function() {
            window.open('/open?path=' + $(this).parent().attr('path'), '_blank');
        });

        $('.file-name').click(function() {
            window.location.href = '/open?path=' + $(this).parent().attr('path');
        });


        // Adding hover effect to all files, folders and upload-button

        $('td, .upload-button').hover(
            function() { $(this).css({ 'color': 'blue' }); },
            function() { $(this).css({ 'color': 'black' }); }
        );

        // Adding hover effect to all file-download and folder-open icons

        $('.file-download').hover(
            function() { $(this).find('img').attr('src', '/static/images/icons/downicon-active.png'); },
            function() { $(this).find('img').attr('src', '/static/images/icons/downicon.jpg'); }
        );

        $('.folder-open').hover(
            function() { $(this).find('img').attr('src', '/static/images/icons/openicon-active.png'); },
            function() { $(this).find('img').attr('src', '/static/images/icons/openicon.jpg'); }
        );


        if (!refreshThumbnails) return;

        // Collecting lines of all "filepath" and "thumbid" for thumbnails

        let lines = $('.items #file-pannel').find('.item tr').toArray().map(function(tr) {
            let filepath = $(tr).attr('path');
            let thumbid = $(tr).find('.file-icon .item-icon').attr('id');
            return '("' + filepath + '", ' + '"' + thumbid + '")';
        });

        // Posting lines to get thumbnails as {thumbid: thumbnails} for all applicable files

        $.post('/thumbnails?path=' + path, lines.join('\n'), function(recieved) {
            recieved.thumbnails.forEach(function(thumbnail) {
                let img = document.getElementById(thumbnail.thumbid);
                if (img) $(img).attr('src', thumbnail.thumbpath);
            });
        });
    }


    // Getting path parameter of this page and loading items into body

    let path = $(location).attr('href').split('?path=')[1];

    function loadBodyItems(setCookie, searchQuery) {
        let settingsPannel = $('.settings-pannel').html();
        $('.settings-pannel').html('<hr> <div class="empty">Refreshing ...</div>');

        if (setCookie) $('.items').html('<hr> <div class="empty">Refreshing ...</div> <hr>');
        else if (searchQuery) $('.items').html('<hr> <div class="empty">Searching ...</div> <hr>');

        $.get('/body?path=' + path + setCookie + searchQuery, function(recieved, status, xhr) {
            $('.items').hide().html(recieved).fadeTo(300, 1.0);

            if (settingsPannel != '<hr> <div class="empty">Refreshing ...</div>')
                $('.settings-pannel').html(settingsPannel);

            let settings = xhr.getResponseHeader('Settings').split(' ');
            $('.settings-pannel input[name=sort][value=' + settings[0] + ']').attr('checked', true);
            $('.settings-pannel input[name=reverse][value=' + settings[1] + ']').attr('checked', true);
            $('.settings-pannel input[name=hidden]').attr('checked', settings[2] == 'True');

            activateBodyItems();
        });
    }

    loadBodyItems('', '');


    // Click actions for settings button on top-pannel

    $('#settings').click(function() {
        clearSearchResults();
        $('.search-bar').val('');
        $('.search-pannel').hide();

        if ($('.settings-pannel').is(':hidden')) {
            $('#settings img').attr('src', '/static/images/icons/done.png');
            $('#search img').attr('src', '/static/images/icons/close.png');
            $('.settings-pannel').show(300);
        } else {
            $('#settings img').attr('src', '/static/images/icons/settings.png');
            $('#search img').attr('src', '/static/images/icons/search.png');
            $('.settings-pannel').hide(300);

            let sortby = $('.settings-pannel input[name=sort]:checked').val();
            let reverse = $('.settings-pannel input[name=reverse]:checked').val();
            let showhidden = $('.settings-pannel input[name=hidden]').prop('checked') ? 'True' : 'False';
            loadBodyItems('&cookie=' + sortby + ' ' + reverse + ' ' + showhidden, '');
        }
    });


    // Search results cleaner function

    let bodyItems = '';

    function clearSearchResults() {
        if (bodyItems) {
            $('.items').html(bodyItems);
            activateBodyItems(false);
            bodyItems = '';
        } else {
            $('.items .item-gap, .items .item').show();
            $('#no-match').remove();
        }
    }


    // Reload body items for every click on deep-search checkbox

    $('#deep').click(function() {
        let placeHolder = $(this).prop('checked') ? 'Search this page recursively' : 'Search items on this page';
        $('.search-bar').attr('placeholder', placeHolder);
        clearSearchResults();
    });


    // Click actions for search button on top-pannel

    $('#search').click(function() {
        if (!$('.settings-pannel').is(':hidden')) {
            $('#settings img').attr('src', '/static/images/icons/settings.png');
            $('#search img').attr('src', '/static/images/icons/search.png');
            $('.settings-pannel').hide(300);
            return;
        }

        if ($('.search-pannel').is(':hidden')) {
            if (!bodyItems) bodyItems = $('.items').html();
            $('#search img').attr('src', '/static/images/icons/close.png');
            $('.search-pannel').show(300);
        } else {
            clearSearchResults();
            $('.search-bar').val('');
            $(this).find('img').attr('src', '/static/images/icons/search.png');
            $('.search-pannel').hide(300);
        }
    });


    // Search actions for search bar

    $('.search-bar').on('keyup', function(event) {
        if (!$(this).val()) clearSearchResults();
        if (event.keyCode != 13) return;

        let query = $(this).val().toLowerCase();

        if ($('#deep').prop('checked') && query) {
            if (!bodyItems) bodyItems = $('.items').html();
            loadBodyItems('', '&search=' + query);
            return;
        } else clearSearchResults();


        // Hidding out items on this page whose name don't include the given query

        $('#folder-pannel, #file-pannel').find('.item').toArray().forEach(function(item) {
            if (!$(item).find('tr .item-name').text().toLowerCase().includes(query)) $(item).hide().next().hide();
        });

        let p = 0;

        $('.items').find('*:visible').toArray().forEach(function(element) {
            if ($(element).attr('class') == 'item') p = 1;
            else if ($(element).attr('class') == 'item-gap') p--;
            if (p < 0) {
                $(element).hide();
                p++;
            }
        });

        let visibleItems = $('.items .item:visible').toArray().length;
        let visibleGaps = $('.items .item-gap:visible').toArray().length;

        if (visibleItems == visibleGaps) $('.items .item-gap:visible').last().hide();
        if (!visibleItems) $('.items hr:last-child').before('<div class="empty" id="no-match">No Match Found !</div>');
    });


    // Dimming everything while file uploading is in progress

    $('#uploader').on('submit', function() {
        $('.settings-pannel, .search-pannel').hide();
        $('.top-pannel, #uploader').fadeTo(300, 0.5);
        $('*').css('pointer-events', 'none');
        $('.items').html('<hr> <br> <div class="empty">Uploading ...</div> <br> <hr>');
        $('.empty').css('color', '#3F3F3F');
    });

});