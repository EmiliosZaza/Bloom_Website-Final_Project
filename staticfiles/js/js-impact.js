// Impact page JS

$(function () {

    // Live tree count from Django context via data attribute
    const bloomData  = document.querySelector('#bloomData');
    const totalTrees = bloomData ? parseInt(bloomData.dataset.totalTrees || '0') : 0;

    // Milestone Tracker
    const GOAL = 1000000;
    const pct  = Math.min((totalTrees / GOAL) * 100, 100);

    $('#milestoneFill').css('width', pct + '%');
    $('#milestoneMarker').css('left', pct + '%');
    $('#milestoneLabel').text(totalTrees.toLocaleString() + ' trees');
    $('#milestoneTitle').closest('[role="progressbar"]').attr('aria-valuenow', totalTrees);

    // Mark ticks when reached
    $('.milestone-tick').each(function () {
        const tickPct = parseFloat($(this).attr('style').replace('left:', '').replace('%', ''));
        if (pct >= tickPct) $(this).find('.milestone-tick_dot').addClass('milestone-tick_dot--reached');
    });

    // Before and After Slider
    const $container = $('#baContainer');
    const $before    = $('#baBefore');
    const $handle    = $('#baHandle');
    let   dragging   = false;
    let   currentPct = 50;

    function setSlider(newPct, animate) {
        currentPct = Math.max(0, Math.min(100, newPct));
        if (animate) {
            $before.css('transition', 'clip-path .4s ease');
            $handle.css('transition', 'left .4s ease');
        } else {
            $before.css('transition', 'none');
            $handle.css('transition', 'none');
        }
        $before.css('clip-path', 'inset(0 ' + (100 - currentPct) + '% 0 0)');
        $handle.css('left', currentPct + '%');
        $handle.attr('aria-valuenow', Math.round(currentPct));
    }

    function getPct(clientX) {
        const rect = $container[0].getBoundingClientRect();
        return ((clientX - rect.left) / rect.width) * 100;
    }

    // Mouse events
    $handle.on('mousedown', function (e) { e.preventDefault(); dragging = true; });
    $(document).on('mousemove', function (e) { if (dragging) setSlider(getPct(e.clientX), false); });
    $(document).on('mouseup',   function ()  { dragging = false; });

    // Keyboard
    $handle.on('keydown', function (e) {
        if (e.key === 'ArrowLeft')  setSlider(currentPct - 5, false);
        if (e.key === 'ArrowRight') setSlider(currentPct + 5, false);
    });

    // Toggle buttons
    $('#baToggleBefore').on('click', function () {
        setSlider(100, true);
        $(this).addClass('ba-toggle_btn--active').attr('aria-pressed', 'true');
        $('#baToggleAfter').removeClass('ba-toggle_btn--active').attr('aria-pressed', 'false');
    });

    $('#baToggleAfter').on('click', function () {
        setSlider(0, true);
        $(this).addClass('ba-toggle_btn--active').attr('aria-pressed', 'true');
        $('#baToggleBefore').removeClass('ba-toggle_btn--active').attr('aria-pressed', 'false');
    });

    setSlider(50, false);

    // Flip Cards
    const co2     = Math.round((totalTrees * 22) / 1000);              // tonnes (22kg per tree per year)
    const sqm = Math.round((totalTrees / 1600) * 10000);               // hectares → square metres
    const people  = (totalTrees * 2).toLocaleString();                 // 1 tree = oxygen for 2 people/year

    $('#flipCo2').text(co2.toLocaleString());
    $('#flipSqm').text(sqm.toLocaleString());
    $('#flipPeople').text(people);
    $('#flipTreeCount').text(totalTrees.toLocaleString() + '+');

});