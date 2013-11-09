$(function(){
	$('.rating a').click(function() {

        var parent = $(this).parents('.rating');
        var vote_class = $(this).attr('class');

        $.get($(this).attr('href'), {}, function(data) {
            console.log(data);
            console.log(data.added);

            if (data.added) {
                console.log('huhuh');
                
                parent.find('a').replaceWith(function() {
                    return $('<span/>', {
                        class: $(this).attr('class'),
                        html: this.innerHTML
                    });
                });
                var count = parseInt(parent.find('span.'+vote_class).find('.votes_count').text());
                var value = parseInt(data.value);
                parent.find('span.'+vote_class).addClass('selected').find('.votes_count').text(count + value);
            }
        });

        return false;
    });
});