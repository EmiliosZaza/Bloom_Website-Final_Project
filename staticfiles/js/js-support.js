// Support page: shop, donate, product modal, cart, wishlist.

$(function () {

    const bloomDataEl      = document.querySelector('[data-trees-dollar]');
    const TREES_PER_DOLLAR = bloomDataEl ? parseInt(bloomDataEl.dataset.treesDollar, 10) : 5;
    const csrfToken        = $('[name=csrfmiddlewaretoken]').val();

    // Product Quick View Modal
    let activeProductId = null;

    $(document).on('click', '.product-card_view-btn, .product-card_img', function (e) {
        if ($(e.target).closest('.product-card_wishlist').length) return;
        const productId = $(this).closest('.product-card').data('product-id')
                          || $(this).data('product-id');
        if (productId) openProductModal(productId);
    });

    function openProductModal(productId) {
        activeProductId = productId;
        $.getJSON('/shop/product/' + productId + '/detail/', function (data) {
            $('#productModalImg').attr('src', data.image || '').attr('alt', data.name);
            $('#productModalCategory').text(data.category);
            $('#productModalTitle').text(data.name);
            $('#productModalPrice').text('$' + parseFloat(data.price).toFixed(2));
            $('#productModalDesc').text(data.description);

            let $treesLine = $('#productModalTrees');
            if (!$treesLine.length) {
                $treesLine = $('<p id="productModalTrees" style="font-size:.82rem;color:var(--green);font-weight:600;margin:0;"></p>');
                $('#productModalPrice').after($treesLine);
            }
            $treesLine.text('🌳 Plants ' + data.trees + ' trees');
            $('#productModalRating').text(data.avg_rating ? '★ ' + data.avg_rating + ' / 5' : '');

            const $wBtn = $('#productModalWishlist');
            if (data.wishlisted) {
                $wBtn.addClass('wishlisted').find('svg').attr('fill', 'currentColor');
            } else {
                $wBtn.removeClass('wishlisted').find('svg').attr('fill', 'none');
            }

            if (data.similar && data.similar.length) {
                const $grid = $('#productModalSimilarGrid').empty();
                data.similar.forEach(function (p) {
                    $grid.append(
                        '<div class="similar-item" data-product-id="' + p.id + '">' +
                        '<img src="' + (p.image || '') + '" alt="' + p.name + '" />' +
                        '<div class="similar-item_name">' + p.name + '</div>' +
                        '<div class="similar-item_price">$' + parseFloat(p.price).toFixed(2) + '</div>' +
                        '</div>'
                    );
                });
                $('#productModalSimilar').show();
            } else {
                $('#productModalSimilar').hide();
            }

            // Reviews list
            const $reviewsList = $('#productModalReviewsList');
            if ($reviewsList.length) {
                $reviewsList.empty();
                if (data.reviews && data.reviews.length) {
                    data.reviews.forEach(function (r) {
                        const stars = '★'.repeat(r.stars) + '☆'.repeat(5 - r.stars);
                        $reviewsList.append(
                            '<div class="product-review-item">' +
                            '<div class="product-review-item_header">' +
                            '<span class="product-review-item_user">' + r.username + '</span>' +
                            '<span class="product-review-item_stars" style="color:var(--green);">' + stars + '</span>' +
                            '<span class="product-review-item_date" style="font-size:.72rem;color:var(--text3);">' + r.date + '</span>' +
                            '</div>' +
                            (r.text ? '<p class="product-review-item_text" style="font-size:.84rem;color:var(--text2);margin:4px 0 0;">' + r.text + '</p>' : '') +
                            '</div>'
                        );
                    });
                    $('#productModalReviewsSection').show();
                } else {
                    $('#productModalReviewsSection').hide();
                }
            }

            // Review form 
            const $reviewForm = $('#productModalReviewSection');
            if ($reviewForm.length) {
                if (data.user_review) {
                    // Show their existing review instead of the form
                    $reviewForm.html(
                        '<p style="font-size:.82rem;color:var(--text3);margin:0;">Your review: ' +
                        '<span style="color:var(--green);">' + '★'.repeat(data.user_review.stars) + '</span>' +
                        (data.user_review.text ? ' — ' + data.user_review.text : '') +
                        '</p>'
                    );
                } else {
                    resetStars();
                    $reviewForm.html($reviewForm.data('original-html') || $reviewForm.html());
                    $reviewForm.show();
                }
            }

            bloomModal.open('#productModalBackdrop', '#productModal');
        });
    }

    // Store original review form HTML on first load
    $(document).ready(function () {
        const $rf = $('#productModalReviewSection');
        if ($rf.length) $rf.data('original-html', $rf.html());
    });

    $(document).on('click', '.similar-item', function () {
        openProductModal($(this).data('product-id'));
    });

    function closeProductModal() {
        bloomModal.close('#productModalBackdrop', '#productModal');
        activeProductId = null;
    }
    $('#productModalClose').on('click', closeProductModal);
    $('#productModalBackdrop').on('click', closeProductModal);
    $(document).on('keydown', function (e) { if (e.key === 'Escape') closeProductModal(); });

    // Add to cart
    $('#productModalAddCart').on('click', function () {
        if (!activeProductId) return;
        addToCart(activeProductId);
    });

    $(document).on('click', '.product-card_cart-btn[data-product-id]', function () {
        addToCart($(this).data('product-id'));
    });

    function addToCart(productId) {
        $.ajax({
            url:    '/shop/add/' + productId + '/',
            method: 'POST',
            data:   { csrfmiddlewaretoken: csrfToken },
            success: function (data) {
                if (data.success) {
                    showCartToast('Added to cart!');
                    updateCartBadge(data.cart_count);
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) $(document).trigger('requireAuth', ['login']);
            }
        });
    }

    function showCartToast(message) {
        let $toast = $('#cartToast');
        if (!$toast.length) {
            $toast = $('<div class="cart-toast" id="cartToast"></div>').appendTo('body');
        }
        $toast.text(message).addClass('visible');
        setTimeout(() => $toast.removeClass('visible'), 2200);
    }

    function updateCartBadge(count) {
        let $badge = $('.nav-cart_badge');
        if (count > 0) {
            if (!$badge.length) {
                $('.nav-cart').append('<span class="nav-cart_badge">' + count + '</span>');
            } else {
                $badge.text(count);
            }
        }
    }

    // Wishlist toggle
    $(document).on('click', '.product-card_wishlist', function (e) {
        e.stopPropagation();
        toggleWishlist($(this).data('product-id'), $(this));
    });

    $('#productModalWishlist').on('click', function () {
        if (!activeProductId) return;
        toggleWishlist(activeProductId, $(this));
    });

    function toggleWishlist(productId, $btn) {
        $.ajax({
            url:    '/shop/wishlist/' + productId + '/',
            method: 'POST',
            data:   { csrfmiddlewaretoken: csrfToken },
            success: function (data) {
                if (data.wishlisted) {
                    $btn.addClass('wishlisted').find('svg').attr('fill', 'currentColor');
                } else {
                    $btn.removeClass('wishlisted').find('svg').attr('fill', 'none');
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) $(document).trigger('requireAuth', ['login']);
            }
        });
    }

    // Star rating
    function resetStars() {
        $('#starRating .star-btn').removeClass('active');
        $('#reviewText').val('');
    }

    $(document).on('click', '.star-btn', function () {
        const stars = parseInt($(this).data('star'));
        $('#starRating .star-btn').each(function (i) {
            $(this).toggleClass('active', i < stars);
        });
    });

    $('#submitReviewBtn').on('click', function () {
        const stars = $('#starRating .star-btn.active').length;
        if (!stars) { alert('Please select a star rating.'); return; }
        const text = $('#reviewText').val().trim();

        $.ajax({
            url:    '/catalogue/review/' + activeProductId + '/',
            method: 'POST',
            data:   { stars: stars, text: text, csrfmiddlewaretoken: csrfToken },
            success: function () {
                showCartToast('Review submitted!');
                $('#productModalReviewSection').html(
                    '<p style="font-size:.82rem;color:var(--text3);margin:0;">Your review: ' +
                    '<span style="color:var(--green);">' + '★'.repeat(stars) + '</span>' +
                    (text ? ' — ' + text : '') +
                    '</p>'
                );
            },
            error: function () { showCartToast('Could not submit review.'); }
        });
    });

    const hash = window.location.hash;
    if (hash && hash.startsWith('#product-')) {
        const productId = parseInt(hash.replace('#product-', ''));
        if (productId) openProductModal(productId);
    }

    // Donate Form

    $(document).on('click', '.donate-amount-btn', function () {
        const amount = $(this).data('amount');
        $('#donateAmount').val(amount);
        $('.donate-amount-btn').removeClass('active');
        $(this).addClass('active');
        updateTreesHint(amount);
    });

    $('#donateAmount').on('input', function () {
        const amount = parseFloat($(this).val()) || 0;
        updateTreesHint(amount);
        $('.donate-amount-btn').each(function () {
            $(this).toggleClass('active', parseFloat($(this).data('amount')) === amount);
        });
    });

    function updateTreesHint(amount) {
        $('#donateTreesCount').text(Math.floor(amount * TREES_PER_DOLLAR).toLocaleString());
    }

    let pendingDonation = null;

    //  Step 1: validate and show confirmation modal 
    $('#donateForm').on('submit', function (e) {
        e.preventDefault();
        const amount  = parseFloat($('#donateAmount').val());
        const message = $('#donateMessage').val().trim();
        const $err    = $('#donateAmountError');

        if (!bloomValidate.isValidNumber(amount, 1, 10000)) {
            $err.text(amount < 1 ? 'Minimum donation is $1.' : 'Maximum donation is $10,000.').addClass('visible');
            return;
        }
        $err.removeClass('visible');

        const trees = Math.floor(amount * TREES_PER_DOLLAR);
        pendingDonation = { amount, message };

        $('#donateConfirmAmount').text('$' + amount.toFixed(2));
        $('#donateConfirmTrees').text(trees.toLocaleString() + ' trees');
        $('#donateConfirmModal, #donateConfirmBackdrop').show();
    });

    // Step 2: confirmed - process the donation 
    $('#donateConfirmYes').on('click', function () {
        if (!pendingDonation) return;
        $('#donateConfirmModal, #donateConfirmBackdrop').hide();

        $.ajax({
            url:    '/donations/donate/',
            method: 'POST',
            data: {
                amount:              pendingDonation.amount,
                message:             pendingDonation.message,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (data) {
                if (data.success) {
                    $('#donateSuccessAmount').text('$' + parseFloat(data.amount).toFixed(2));
                    $('#donateSuccessTrees').text(data.trees_equivalent.toLocaleString() + ' trees');
                    $('#donateSuccessModal, #donateSuccessBackdrop').show();
                    $('#donateForm')[0].reset();
                    $('.donate-amount-btn').removeClass('active');
                    updateTreesHint(0);
                    pendingDonation = null;
                }
            },
            error: function (xhr) {
                const resp = xhr.responseJSON;
                if (xhr.status === 403) {
                    $(document).trigger('requireAuth', ['login']);
                } else {
                    $('#donateAmountError').text((resp && resp.error) || 'Something went wrong.').addClass('visible');
                }
                pendingDonation = null;
            }
        });
    });

    // Step 2: cancelled 
    $('#donateConfirmNo').on('click', function () {
        $('#donateConfirmModal, #donateConfirmBackdrop').hide();
        pendingDonation = null;
    });

    $('#donateSuccessClose').on('click', function () {
        $('#donateSuccessModal, #donateSuccessBackdrop').hide();
    });

});