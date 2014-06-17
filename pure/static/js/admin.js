(function(){
    $(document).ready(function(){
        var postForm = $('.post-form');

        if (postForm.length > 0 ) {
            var saveBtn = $('.save');
            var save_post = function() {
                var postData = {};
                $('input',postForm).each(function(){
                    postData[$(this).attr('name')] = $(this).val();
                }); 
                postData['markdown'] = editor.getValue();
                saveBtn.val('保存...').css('background-color','red');

                $.post(postForm.attr('action'),postData,function(){
                    setTimeout(function(){
                        saveBtn.val('保存').css('background-color','#3276b1');
                    },500);
                });
            };

            var editor = CodeMirror.fromTextArea(document.getElementById('editor'),{
                viewportMargin:Infinity,
            });
            var id = $('input[name=id]');
            if (id.val() > 0) {
                setInterval(save_post,10000);
            }
            $(window).bind('keydown', function(event) {
                if (event.ctrlKey || event.metaKey) {
                    if (String.fromCharCode(event.which).toLowerCase() == 's') {
                        event.preventDefault();
                        save_post();
                    }
                }
            });
        }
    });
})(jQuery)
