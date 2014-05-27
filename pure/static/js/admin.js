(function(){
    $(document).ready(function(){
        var postForm = $('.post-form');
        if (postForm.length > 0) {

            var editor = CodeMirror.fromTextArea(document.getElementById('editor'),{
                viewportMargin:Infinity,
            });
            setInterval(function(){
                var postData = {};
                $('input',postForm).each(function(){
                    postData[$(this).attr('name')] = $(this).val();
                }); 
                postData['markdown'] = editor.getValue();
                $.post(postForm.attr('action'),postData,function(){});
            },10000);
        }
    });
})(jQuery)
