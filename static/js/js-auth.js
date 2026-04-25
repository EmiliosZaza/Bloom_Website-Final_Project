// Auth modal — login / register tab switching and validation
// Requires jQuery 3.6+

$(function () {

    const $backdrop = $('#authBackdrop');
    const $modal    = $('#authModal');

    // ── Open modal ────────────────────────────────────────────
    function openAuth(tab) {
        $backdrop.addClass('visible');
        $modal.addClass('visible');
        $('body').css('overflow', 'hidden');
        switchTab(tab || 'login');
        setTimeout(() => $modal.find('.auth-panel.active input:first').focus(), 100);
    }

    // ── Close modal ───────────────────────────────────────────
    function closeAuth() {
        $backdrop.removeClass('visible');
        $modal.removeClass('visible');
        $('body').css('overflow', '');
    }

    // ── Switch tabs ───────────────────────────────────────────
    function switchTab(tab) {
        if (tab === 'login') {
            $('#tabLogin').addClass('active').attr('aria-selected', 'true');
            $('#tabRegister').removeClass('active').attr('aria-selected', 'false');
            $('#panelLogin').addClass('active');
            $('#panelRegister').removeClass('active');
        } else {
            $('#tabRegister').addClass('active').attr('aria-selected', 'true');
            $('#tabLogin').removeClass('active').attr('aria-selected', 'false');
            $('#panelRegister').addClass('active');
            $('#panelLogin').removeClass('active');
        }
    }

    $(document).on('click', '[data-auth-trigger]', function () {
        openAuth($(this).data('auth-trigger'));
    });

    $('#tabLogin').on('click',    () => switchTab('login'));
    $('#tabRegister').on('click', () => switchTab('register'));

    $('#authModalClose').on('click', closeAuth);
    $backdrop.on('click', closeAuth);
    $(document).on('keydown', function (e) { if (e.key === 'Escape') closeAuth(); });

    const params = new URLSearchParams(window.location.search);
    if (params.has('open_auth')) openAuth(params.get('open_auth'));

    $(document).on('requireAuth', function (e, tab) { openAuth(tab || 'login'); });

    // ── Demo credential cards ─────────────────────────────────
    $(document).on('click', '.demo-credential-card', function () {
        $('#loginUsername').val($(this).data('username'));
        $('#loginPassword').val($(this).data('password'));
        clearError('#loginUsernameError', '#loginUsername');
        clearError('#loginPasswordError', '#loginPassword');
        $('#loginUsername').focus();
    });

    // ── Login validation ──────────────────────────────────────
    $('#loginForm').on('submit', function (e) {
        let ok = true;

        const username = $('#loginUsername').val().trim();
        if (!username) {
            showError('#loginUsernameError', 'Please enter your username.');
            ok = false;
        } else {
            clearError('#loginUsernameError', '#loginUsername');
        }

        const password = $('#loginPassword').val();
        if (!password) {
            showError('#loginPasswordError', 'Please enter your password.');
            ok = false;
        } else {
            clearError('#loginPasswordError', '#loginPassword');
        }

        if (!ok) e.preventDefault();
    });

    // ── Register validation ───────────────────────────────────
    $('#registerForm').on('submit', function (e) {
        let ok = true;

        const username = $('#regUsername').val().trim();
        if (!bloomValidate.isValidUsername(username)) {
            showError('#regUsernameError', 'Username may only contain letters, digits, and @/./+/-/_'); ok = false;
        } else { clearError('#regUsernameError', '#regUsername'); }

        const email = $('#regEmail').val().trim();
        if (!bloomValidate.isValidEmail(email)) {
            showError('#regEmailError', 'Please enter a valid email.'); ok = false;
        } else { clearError('#regEmailError', '#regEmail'); }

        const firstName = $('#regFirstName').val();
        if (firstName && !bloomValidate.isValidName(firstName)) {
            showError('#regFirstNameError', 'Name may only contain letters, spaces, and \' . , -'); ok = false;
        } else { clearError('#regFirstNameError', '#regFirstName'); }

        const p1 = $('#regPassword1').val();
        const p2 = $('#regPassword2').val();
        if (!bloomValidate.isValidPassword(p1, 8)) {
            showError('#regPassword1Error', 'Password must be at least 8 characters.'); ok = false;
        } else { clearError('#regPassword1Error', '#regPassword1'); }

        if (p1 !== p2) {
            showError('#regPassword2Error', 'Passwords do not match.'); ok = false;
        } else { clearError('#regPassword2Error', '#regPassword2'); }

        if (!ok) e.preventDefault();
    });

    // ── Live sanitisation ─────────────────────────────────────
    $('#regFirstName').on('input', function () {
        $(this).val(bloomValidate.sanitizeName($(this).val()));
    });

    $('#loginUsername, #loginPassword').on('input', function () {
        clearError('#login' + ($(this).attr('id') === 'loginUsername' ? 'UsernameError' : 'PasswordError'));
    });

    // ── Helpers ───────────────────────────────────────────────
    function showError(errorId, message) {
        $(errorId).text(message).addClass('visible');
    }

    function clearError(errorId, inputId) {
        $(errorId).removeClass('visible');
        if (inputId) $(inputId).removeClass('invalid');
    }

});