function showRegister() {
    document.getElementById("registerForm").style.display = "block";
    document.getElementById("loginForm").style.display = "none";
}

function showLogin() {
    document.getElementById("registerForm").style.display = "none";
    document.getElementById("loginForm").style.display = "block";
}

function generateOTP() {
    fetch('/generate-otp', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        console.log("OTP Response:", data);  // Debugging output
        if (data.otp) {
            document.getElementById("otpMessage").innerText = `Your OTP is: ${data.otp}`;
        } else {
            document.getElementById("otpMessage").innerText = `Error: ${data.error}`;
        }
    })
    .catch(error => console.error("Error fetching OTP:", error));  // Log fetch errors
}
