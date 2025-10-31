# AuthCore: Secure Flask Authentication Server

AuthCore is a full-stack Flask application that provides a secure, backend-driven authentication system. It includes user registration, login with password hashing, password reset, and advanced security features like account lockout after multiple failed attempts.

The application is built with a decoupled frontend-backend architecture:
* **Backend (Flask):** A JSON API that handles all logic and database operations.
* **Frontend (HTML/JS):** A user interface built with Tailwind CSS that consumes the backend API.

## Technical Implementation

### 1. Project Structure

The project follows a standard Flask factory pattern, separating concerns for scalability and maintenance.

### 2. Backend (Flask & SQLAlchemy)

#### `app.py`: App Factory & Routes

* **App Factory (`create_app`):** The application is created using a factory function. This allows for better testing and configuration management.
* **Database Path Fix:** The app factory explicitly constructs an **absolute path** for the `SQLALCHEMY_DATABASE_URI` (e.g., `sqlite:////path/to/project/instance/app.db`). This solves the common `sqlite3.OperationalError: unable to open database file` by ensuring the app and database are aligned, regardless of where the app is run from.
* **Route Separation:** Routes are split into two logical groups:
    1.  **Frontend Page Routes (`@app.route('/')`)**: These routes (`/`, `/login`, `/register`, etc.) are simple `GET` requests that only serve the corresponding HTML templates.
    2.  **Backend API Routes (`@app.route('/api/...')`)**: These routes (`/api/login`, `/api/register`, etc.) are the core of the app. They only accept `POST` (or `GET` for `/api/users`) requests, process JSON data, interact with the database, and return JSON responses. This decouples the logic from the presentation.

#### `models.py`: Database & Extensions

* **Extension Initialization:** This file creates the `db = SQLAlchemy()` and `bcrypt = Bcrypt()` extension objects *without* attaching them to an app. They are initialized later in `app.py`'s factory (`db.init_app(app)`). This prevents circular import errors.
* **`User` Model:** The `User` model defines the database schema and includes all business logic for a user.
    * `set_password(password)`: Uses `bcrypt.generate_password_hash` to create a secure, salted hash.
    * `check_password(password)`: Uses `bcrypt.check_password_hash` to safely compare a plain-text password against the stored hash.
    * **Security Fields (Level 2):**
        * `failed_login_attempts`: An integer counter.
        * `lockout_until`: A `DateTime` field that, if set in the future, indicates the account is locked.
    * `is_locked()`: A helper method that checks if `lockout_until` is valid and in the future.

#### `config.py`: Configuration Management

* This file uses `python-dotenv` to load environment variables from the `.env` file.
* The `Config` class holds all configuration variables, providing a clean and organized way to manage settings like `SECRET_KEY`, `LOCKOUT_ATTEMPTS`, and `LOCKOUT_DURATION_MINUTES`.

#### Security Feature: Account Lockout (Level 2)

This logic is implemented entirely in the `/api/login` route in `app.py`:
1.  **Check for Lock:** When a user is found, the app first calls `user.is_locked()`. If true, it immediately returns a `403 Forbidden` error.
2.  **Handle Invalid Password:** If the password check (`user.check_password(password)`) fails:
    * The user's `failed_login_attempts` counter is incremented.
    * The app checks if this counter has reached the limit from `app.config['LOCKOUT_ATTEMPTS']`.
    * If it has, `lockout_until` is set to the current time plus the `LOCKOUT_DURATION_MINUTES`.
    * The database session is committed.
3.  **Handle Successful Login:** On a successful login, `failed_login_attempts` is reset to `0` and `lockout_until` is set to `None` to clear any existing lock.

### 3. Frontend (Tailwind & JavaScript)

#### `base.html`: The Core Layout

* **Tailwind CSS:** Tailwind is loaded directly from its CDN. This avoids a complex `npm` build step. The configuration (`tailwind.config`) and a few custom styles (for error messages and dark-mode inputs) are defined in `<script>` and `<style>` tags directly in the `<head>`.
* **Dark Mode:** The app is set to `class="dark"` by default.
* **Mobile-First Navbar:** The navbar includes two separate menus: a full-size one (`hidden md:flex`) and a mobile one (`hidden md:hidden`). The `mobile-menu-button` toggles the visibility of the mobile menu.

#### `static/script.js`: Client-Side Logic

This file handles all user interactions and communication with the backend API.
1.  **Event Listeners:** The script waits for the `DOMContentLoaded` event. It then attaches `submit` event listeners to all forms (`#register-form`, `#login-form`, `#reset-form`).
2.  **API Communication (`fetch`):**
    * When a form is submitted, `preventDefault()` is called to stop the page from reloading.
    * `new FormData(form)` and `Object.fromEntries()` are used to create a simple JavaScript object from the form data.
    * The `fetch` API is used to `POST` this object (as a JSON string) to the corresponding `/api/...` endpoint.
3.  **Response Handling:**
    * The script `await`s the JSON response from the server.
    * The `showMessage(message, isError)` helper function is used to display success or error messages to the user in the `#message` div.
    * On the `/users` page, an `async` function `fetchUsers` makes a `GET` request to `/api/users`, parses the JSON array, and dynamically builds the HTML table in the `#users-tbody`.
4.  **Mobile Menu Toggle:** A simple event listener is added to the `.mobile-menu-button` to toggle the `.hidden` class on the `#mobile-menu` div.

## How to Run

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/ilnurkkh/AuthCore.git](https://github.com/ilnurkkh/AuthCore.git)
    cd AuthCore
    ```

2.  **Create a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create the `.env` file:**
    Create a file named `.env` in the root of the project and add your secret key:
    ```
    SECRET_KEY='your-very-strong-and-secret-key-goes-here'
    ```

5.  **Run the application:**
    ```sh
    python app.py
    ```

The application will be running at `http://127.0.0.1:5000`.
