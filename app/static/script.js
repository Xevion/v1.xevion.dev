console.log('Loaded');
$('.delete').each(function (e) {
    console.log('Each');
    $(this).click(function() {
        $(this).parent().parent().fadeOut();
        console.log('Parent');
    });
});

console.log('1');
$('.delete').click(function () {
    console.log('Received Click');
});

// Close mobile & tablet menu on item click
$('.navbar-item').each(function (e) {
    $(this).click(function () {
        if ($('#navbar-burger-id').hasClass('is-active')) {
            $('#navbar-burger-id').removeClass('is-active');
            $('#navbar-menu-id').removeClass('is-active');
        }
    });
});

 // Open or Close mobile & tablet menu
$('#navbar-burger-id').click(function () {
    console.log("hit")
    if ($('#navbar-burger-id').hasClass('is-active')) {
        $('#navbar-burger-id').removeClass('is-active');
        $('#navbar-menu-id').removeClass('is-active');
    } else {
        $('#navbar-burger-id').addClass('is-active');
        $('#navbar-menu-id').addClass('is-active');
    }
});
