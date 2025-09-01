# Akua

Akua is a tourism web platform designed to help users discover destinations, cultural events, and local experiences in an organized and interactive way.  

## Team Members
- Dorian Guisado  
- Julian Lara  
- Luis Alfonso Agudelo  
- Gina Valencia  
- Adyuer Ojeda  

## Initial Setup

1. **Clone Repository**
    ```bash
    git clone https://github.com/Luisagudelo372/Akua.git
    cd Akua
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

5. **Run Development Server**
    ```bash
    python manage.py runserver
    ```
    The application will run at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---
