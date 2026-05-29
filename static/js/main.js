const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Sliding Panel Toggles
signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

// Helper function to get CSRF token reliably
function getCSRFToken() {
    // 1. Try the global variable we defined in the template
    if (typeof CSRF_TOKEN !== 'undefined') return CSRF_TOKEN;

    // 2. Try the hidden input field in the form
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;

    // 3. Fallback to cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 1. Handle Inbox Login (Step 1)
const inboxLoginForm = document.getElementById('inbox-login-form');
const otpForm = document.getElementById('otp-form');
const inboxError = document.getElementById('inbox-error');
const otpError = document.getElementById('otp-error');

if (inboxLoginForm) {
    inboxLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const btn = document.getElementById('btn-inbox-login');
        const loader = btn.querySelector('.loader-icon');
        const btnText = btn.querySelector('span');

        // UI State: Loading
        btn.disabled = true;
        loader.style.display = 'inline-block';
        btnText.style.opacity = '0.5';
        inboxError.style.display = 'none';

        const formData = new FormData(inboxLoginForm);

        try {
            const response = await fetch(INBOX_LOGIN_URL, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                console.log("OTP Sent Successfully, switching forms...");
                // Success: Switch to OTP Form
                inboxLoginForm.classList.remove('active-form');
                inboxLoginForm.classList.add('hidden-form');
                otpForm.classList.remove('hidden-form');
                otpForm.classList.add('active-form');
                console.log("Forms switched!");
            } else {
                inboxError.textContent = data.message;
                inboxError.style.display = 'block';
            }
        } catch (error) {
            alert("Network/Server Error: " + error.message);
            inboxError.textContent = "Request Failed: " + error.message;
            inboxError.style.display = 'block';
        } finally {
            btn.disabled = false;
            loader.style.display = 'none';
            btnText.style.opacity = '1';
        }
    });
}

// 2. Handle OTP Verification (Step 2)
async function handleVerify(e) {
    if (e) e.preventDefault();
    console.log("Nuclear Option: handleVerify called!");

    const verifyBtn = document.getElementById('btn-verify-otp');
    const loader = verifyBtn.querySelector('.loader-icon');
    const btnText = verifyBtn.querySelector('span');
    const otpError = document.getElementById('otp-error');

    // Collect OTP from boxes
    const otpBoxes = document.querySelectorAll('.otp-box');
    let otpValue = "";
    otpBoxes.forEach(box => otpValue += box.value);

    if (otpValue.length < 6) {
        alert("Please enter all 6 digits.");
        return;
    }

    // UI State: Loading
    verifyBtn.disabled = true;
    if (loader) loader.style.display = 'inline-block';
    if (btnText) btnText.style.opacity = '0.5';
    otpError.style.display = 'none';

    const formData = new FormData();
    formData.append('otp', otpValue);

    try {
        console.log("Sending OTP for verification...");
        const response = await fetch(VERIFY_OTP_URL, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Full Container Success Animation
            const containerBox = document.getElementById('container');
            // Dashboard page needs to open like an animation
            // Fade out the current login page smoothly
            document.body.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            document.body.style.opacity = '0';
            document.body.style.transform = 'scale(0.98)';
            
            // Redirect right as the fade out finishes
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 400);
        } else {
            otpError.textContent = data.message;
            otpError.style.display = 'block';
            verifyBtn.disabled = false;
            if (loader) loader.style.display = 'none';
            if (btnText) btnText.style.opacity = '1';
        }
    } catch (error) {
        alert("Verification Error: " + error.message);
        verifyBtn.disabled = false;
        if (loader) loader.style.display = 'none';
        if (btnText) btnText.style.opacity = '1';
    }
}

// Auto-focus logic for OTP boxes
const otpInputs = document.querySelectorAll('.otp-box');
otpInputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        if (e.target.value.length === 1 && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
            if (e.target.value === '' && index > 0) {
                // Focus previous box and clear its value automatically
                otpInputs[index - 1].focus();
                otpInputs[index - 1].value = '';
                e.preventDefault();
            }
        }
    });
});