$(function(){
	$('.arrows a').click(function() {
        var arrow = $(this);
        var index = arrow.find('i').hasClass('icon-arrow-up') ? 1 : 0;
        var container = arrow.parent().parent();
        var form = container.find('form');

        form.find('input:radio')[index].checked = true;

        $.post(form.attr('action'), form.serialize(), function(data) {
            if (data.location) {
                location = data.location;
            } else {
                container.find('.score').text(data.rating_sum);
            }
        }, 'json');

        return false;
    });
});