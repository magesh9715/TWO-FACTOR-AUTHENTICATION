# 🔐 Two-Factor Authentication (2FA) System – Flask + MySQL

This project is a secure web-based Two-Factor Authentication (2FA) system built using **Python (Flask)**, **MySQL**, **HTML/CSS**, and **JavaScript**. It includes student registration, login with CAPTCHA, OTP-based verification (via email or QR code), and a personalized student dashboard.

## 🚀 Features

* 📝 **User Registration**

  * Fields: Name, Email, Department, CGPA, Password
  * Strong password validation + CAPTCHA

* 🔐 **Secure Login**

  * Username, Password, CAPTCHA
  * Forgot Password option

* 🔄 **Two-Factor Authentication**

  * OTP verification via **Email** or **QR Code**
  * Time-based or session-based OTP for added security

* 🎓 **Student Dashboard**

  * Displays profile (Name, Email, Department, CGPA)
  * Change Password and Logout functionality

## 🛠️ Tech Stack

* **Frontend**: HTML, CSS, JavaScript
* **Backend**: Python (Flask)
* **Database**: MySQL
* **Security**: OTP, CAPTCHA, Hashed Passwords

## 📂 Folder Structure

```
2FA-System/
├── app.py
├── templates/
│   ├── register.html
│   ├── login.html
│   ├── verify_otp.html
│   └── dashboard.html
├── static/
│   ├── css/
│   └── js/
├── db/
│   └── init_db.sql
└── utils/
    └── otp_generator.py
```

## ⚙️ Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/2fa-flask-system.git
   ```

2. Set up the MySQL database using `init_db.sql`.

3. Update your **Flask config** with your database and email credentials.

4. Run the Flask server:

   ```bash
   python app.py
   ```

5. Access the system at:

   ```
   http://localhost:5000
   ```

## 🔐 Security Highlights

* Passwords stored using hashing (bcrypt or SHA-256)
* OTPs expire after a short time for protection
* CAPTCHA to prevent bots
* Unique email and user ID validation

## 👨‍💻 Author

* magesh (https://github.com/magesh9715)

## 📄 License

This project is licensed under the MIT License.
