// Contact page logic. Requires jQuery 3.6+.

$(function () {

    const $nameInput    = $('#contactName');
    const $emailInput   = $('#contactEmail');
    const $subjectInput = $('#contactSubject');
    const $messageInput = $('#contactMessage');

    function validate() {
        let ok = true;

        const name = $nameInput.val().trim();
        if (!bloomValidate.isValidName(name)) {
            $('#nameError').text("Name may only contain letters, spaces, and ' . , -").addClass('visible');
            $nameInput.addClass('invalid');
            ok = false;
        } else {
            $('#nameError').removeClass('visible');
            $nameInput.removeClass('invalid');
        }

        const email = $emailInput.val().trim();
        if (!bloomValidate.isValidEmail(email)) {
            $('#emailError').text('Please enter a valid email address.').addClass('visible');
            $emailInput.addClass('invalid');
            ok = false;
        } else {
            $('#emailError').removeClass('visible');
            $emailInput.removeClass('invalid');
        }

        const subject = $subjectInput.val().trim();
        if (!bloomValidate.isValidLength(subject, 5, 200)) {
            $('#subjectError').text('Subject must be at least 5 characters.').addClass('visible');
            $subjectInput.addClass('invalid');
            ok = false;
        } else {
            $('#subjectError').removeClass('visible');
            $subjectInput.removeClass('invalid');
        }

        const message = $messageInput.val().trim();
        if (!bloomValidate.isValidLength(message, 10, 1000)) {
            $('#messageError').text('Message must be at least 10 characters.').addClass('visible');
            $messageInput.addClass('invalid');
            ok = false;
        } else {
            $('#messageError').removeClass('visible');
            $messageInput.removeClass('invalid');
        }

        return ok ? { name, email, subject, message } : null;
    }

    // ── Live sanitisation and error clearing ──────────────────
    $nameInput.on('input', function () {
        $(this).val(bloomValidate.sanitizeName($(this).val()));
        if (bloomValidate.isValidName($(this).val())) {
            $('#nameError').removeClass('visible');
            $(this).removeClass('invalid');
        }
    });

    $emailInput.on('input', function () {
        if (bloomValidate.isValidEmail($(this).val().trim())) {
            $('#emailError').removeClass('visible');
            $(this).removeClass('invalid');
        }
    });

    $subjectInput.on('input', function () {
        if (bloomValidate.isValidLength($(this).val().trim(), 5)) {
            $('#subjectError').removeClass('visible');
            $(this).removeClass('invalid');
        }
    });

    $messageInput.on('input', function () {
        if (bloomValidate.isValidLength($(this).val().trim(), 10)) {
            $('#messageError').removeClass('visible');
            $(this).removeClass('invalid');
        }
    });

    // ── Modal ─────────────────────────────────────────────────
    function openModal(data) {
        const rows = [
            ['Name',    data.name],
            ['Email',   data.email],
            ['Subject', data.subject],
            ['Message', data.message],
        ];
        $('#contactSummary').html(
            rows.map(function (f) {
                return '<div class="contact-modal_row"><dt>' + f[0] + '</dt><dd>' + $('<span>').text(f[1]).html() + '</dd></div>';
            }).join('')
        );
        bloomModal.open('#contactModalBackdrop', '#contactModal');
        $('#contactModalClose').focus();
    }

    function closeModal() {
        bloomModal.close('#contactModalBackdrop', '#contactModal');
        $('#contactForm')[0].reset();
        $('.contact-field_error').removeClass('visible');
        $('input, textarea').removeClass('invalid');
    }

    $('#contactForm').on('submit', function (e) {
        e.preventDefault();
        const data = validate();
        if (!data) return;
        openModal(data);
    });

    $('#contactModalClose, #contactModalBackdrop').on('click', closeModal);
    $(document).on('keydown', function (e) { if (e.key === 'Escape') closeModal(); });

});