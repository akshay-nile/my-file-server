$(document).ready(function() {

    // Removing extra .drive-gap hr from drives pannel added by jinja2 templates

    $('#drive-pannel .drive-gap:last-child').remove();

    // If it's a desktop screen then set body's CSS, then show body with fading effect

    if (screen.width > screen.height)
        $('body').css({ 'width': '400px', 'margin': '0px auto', 'overflow': 'scroll' });

    $('body').fadeTo(300, 1.0);

    // Assigning click events to various drives and libs pannel

    $('.drive-name-td, .drive-open-td').click(function() {
        if (!uploading) window.location.href = '/storage?path=' + $(this).parent().attr('path');
    });

    $('.drive-icon-td').click(function() {
        if (!uploading) window.open('/storage?path=' + $(this).parent().attr('path'), '_blank');
    });

    $('#libs .un-selectable').click(function() {
        if (!uploading) window.location.href = '/storage?path=' + $(this).attr('path');
    });

    // Adding hover effect to all td, libs, upload-button and drive-open icons

    $('td, .upload-button').hover(
        function() { if (!uploading) $(this).css({ 'color': 'blue' }); },
        function() { if (!uploading) $(this).css({ 'color': 'black' }); }
    );

    $('.drive-open-td').hover(
        function() { $(this).find('img').attr('src', '/static/images/icons/openicon-active.png'); },
        function() { $(this).find('img').attr('src', '/static/images/icons/openicon.jpg'); }
    );

    // Dimming everything while file uploading is in progress

    $('#uploader').on('submit', function() {
        $('.drives, #libs, .path, hr').fadeTo(300, 0.5);
        $(this).hide().after('<div class="uploading">Uploading ...</div>');
        uploading = true;
    });

});