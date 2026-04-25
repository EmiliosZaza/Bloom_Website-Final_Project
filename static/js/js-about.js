// About page logic. Requires jQuery 3.6+.

$(function () {

    // Testimonial carousel
    const $slides = $('.testimonial-slide');
    const $dots   = $('#testimonialDots');
    const total   = $slides.length;
    let   current = 0;

    // Build dot buttons dynamically from slide count
    $slides.each(function (i) {
        $dots.append(
            $('<button>')
                .addClass('testimonial-dot' + (i === 0 ? ' active' : ''))
                .attr({ role: 'tab', 'aria-label': 'Slide ' + (i + 1) })
                .on('click', function () { goTo(i); })
        );
    });

    const $dotBtns = $dots.find('.testimonial-dot');

    function goTo(index) {
        $slides.eq(current).removeClass('active');
        $dotBtns.eq(current).removeClass('active');
        current = (index + total) % total;
        $slides.eq(current).addClass('active');
        $dotBtns.eq(current).addClass('active');
    }

    $('#testimonialPrev').on('click', function () { goTo(current - 1); });
    $('#testimonialNext').on('click', function () { goTo(current + 1); });

    goTo(0);

});