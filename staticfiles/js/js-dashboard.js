// Dashboard interactions
// Clicking a product card on the dashboard opens it on the Support Us page.

$(function () {

    // Clicking a product card on the dashboard navigates to the Support Us page
    $(document).on('click', '.dashboard-product-card', function () {
        const productId = $(this).data('product-id');
        if (productId) {
            window.location.href = '/shop/support/#product-' + productId;
        }
    });

});
