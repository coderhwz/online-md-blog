(function(){
    $(document).ready(function(){
        var postForm = $('.post-form');
        if (postForm.length > 0) {
            setInterval(function(){
                $.post(postForm.attr('action'),postForm.serialize(),function(){});
            },1000);
        }
    });
})(jQuery)
