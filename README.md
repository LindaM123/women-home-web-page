# 🏡 Women Home – Web Project

This is the final project for **Harvard University’s CS50x**, developed to provide a digital space that supports and connects women through resources, housing, and psychological assistance.

## 🌍 Objective

This platform offers housing services, psychological assistance, and legal advice for women who are living a case of domestic violence in Colombia.

## 🧭 Strategy

Women who are living a case of domestic violence can:
- Find a safe home to live in different places in the country with their children.
- Schedule meetings with psychologists and lawyers to solve their situation.

The houses belong to women volunteers who want to fight against domestic violence in Colombia. They can register their houses on the platform to help others.

## 🧰 Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS
- **Other:** Jinja templates, static assets

## 📁 Project Structure

```
final/
│── application.py           # Main Flask app
│── helpers.py               # Helper functions
│── data.db                  # SQLite database
│── requirements.txt         # Python dependencies
│
├── static/                  # Static assets (images, CSS)
│   ├── styles.css
│   └── ...
│
├── templates/               # HTML templates
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   └── ...
```

## 🚀 Installation and Setup (Linux)

1. **Clone this repository:**
   ```bash
   git clone https://github.com/LindaM123/women-home.git
   cd women-home/final
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set the Flask application environment variable:**
   ```bash
   export FLASK_APP=application.py
   ```

5. *(Optional)* **Enable debug mode for auto-reload:**
   ```bash
   export FLASK_DEBUG=1
   ```

6. **Run the app:**
   ```bash
   flask run
   ```

The application will be available at [http://localhost:5000](http://localhost:5000).

👉 Alternatively, you can also run Flask without setting environment variables:

```bash
flask --app application.py run
```

## 👤 User Features

- Register/Login to the platform  
- Search and register homes for women  
- Access legal and psychological resources  
- View calendar and information pages  

## 🔐 Security

- Passwords are handled securely (not stored in plain text).  
- Basic authentication and session handling.

## 📸 UI Preview

*(You can add screenshots of the homepage or key features here later.)*

## 📝 Acknowledgments

- This project was built as part of the **CS50x** course by Harvard University.  
- Special thanks to the course staff and mentors for their support.
