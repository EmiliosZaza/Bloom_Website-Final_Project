// Cart page JS

$(function () {

    const csrfToken = $('[name=csrfmiddlewaretoken]').val();

    $(document).on('click', '.cart-item_remove', function () {
        const itemId = $(this).data('item-id');
        $.ajax({
            url:    '/shop/remove/' + itemId + '/',
            method: 'POST',
            data:   { csrfmiddlewaretoken: csrfToken },
            success: function (data) {
                $('#cart-item-' + itemId).remove();
                $('#cartTotal').text('$' + parseFloat(data.total).toFixed(2));
                if (data.cart_count === 0) location.reload();
            }
        });
    });

});