// BLOOM — js-dashboard.js | Dashboard interactions
// Clicking a product card on the dashboard opens it on the support page.
// Requires jQuery 3.6+.

$(function () {

    // Clicking a product card on the dashboard navigates to the support page
    // with the product modal pre-opened via a hash parameter
    $(document).on('click', '.dashboard-product-card', function () {
        const productId = $(this).data('product-id');
        if (productId) {
            window.location.href = '/shop/support/#product-' + productId;
        }
    });

});
