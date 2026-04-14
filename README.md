# 🌍 Akua

Akua is a tourism web platform designed to help users discover destinations, cultural events, and local experiences in an organized and interactive way.  

---

##  Team Members
- Dorian Alejandro Guisao Ospina  
- Julian Lara  
- Luis Alfonso Agudelo  
- Gina Valencia  

---

##  Technologies
- [Django 5+](https://www.djangoproject.com/)
- [TailwindCSS](https://tailwindcss.com/) integrated with `django-tailwind`
- [Node.js](https://nodejs.org/) for CSS build tools

---

##  Initial Setup

1. **Clone Repository**
    ```bash
    git clone https://github.com/Luisagudelo372/Akua.git
    cd akua
    ```

2. **Create & Activate Virtual Environment**
    ```bash
    python -m venv venv
    
    # On Windows
    venv\Scripts\activate
    
    # On macOS/Linux
    source venv/bin/activate
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run Database Migrations**
    ```bash
    python manage.py migrate
    ```

5. **Create Superuser (optional)**
    ```bash
    python manage.py createsuperuser
    ```

6. **Install Tailwind (if needed)**
    ```bash
    npm install
    npm run dev   # Run this in a separate terminal to watch styles
    ```

7. **Run Development Server**
    ```bash
    python manage.py runserver
    ```
    The application will run at:  [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---
