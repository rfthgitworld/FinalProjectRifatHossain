### INF601 - Advanced Programming in Python
### Rifat Hossain   
### Final Project
 
***


# Vulnerability Tracker (Django Application)

## Description

The **Vulnerability Tracker** is a comprehensive web application built using the Django framework designed for cybersecurity professionals and enthusiasts. It provides a real-time platform for searching, viewing, and tracking software vulnerabilities (CVEs) by integrating directly with the official **National Vulnerability Database (NVD) API** maintained by the U.S. National Institute of Standards and Technology (NIST).

The application helps users stay informed about recent threats, severity levels, and affected systems, with personalized tracking features and visual analysis tools.

**Key Features:**

* **Real-time Vulnerability Feeds:** The Home Page displays the latest vulnerabilities fetched directly from the NVD API.
* **Search Functionality:** Enables users to search the NVD database by keyword for vulnerabilities reported within the last 120 days.
* **User Authentication:** Secure user registration, login, and logout functionalities.
* **Personal Watchlist:** Authenticated users can bookmark and monitor specific CVEs on their dedicated **My Watchlist** page.
* **Statistics & Trends:** The Statistics Page visualizes vulnerability trends and severity distributions using data charts (Chart.js).
* **Detailed Views:** Separate detail page for each vulnerability displaying full descriptions and scoring information.

***

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Dependencies

This project requires Python 3.x and the following libraries:
* Django
* requests
* django-bootstrap-v5
* python-decouple

You can install all required dependencies using `pip`:

First, navigate into the project directory and install the required Python packages using pip:

```
pip install -r requirements.txt
```

### Initialize the database

Before running the application, you must initialize the database and create an administrative user. Run these commands from the root project directory (where `manage.py` is located):


1. Create initial migration files (if models were modified):

    ```
    python manage.py makemigrations tracker
    ```
2. **Apply migrations to the database:** This command executes the migrations, creating the necessary database tables (and the `db.sqlite3 file`).

   ```
    python manage.py migrate
   ```
3. **Create a Superuser (Administrator):** This command creates the administrator login for your /admin side of the project. Follow the prompts to set a username, email, and password.

   ```
    python manage.py createsuperuser
   ```
   
### Program Execution

Once the database is initialized, you can start the development server

1. **Run the Django Development Server:** Ensure you are in the VulnTrackerProject/ directory.

    ```
    python manage.py runserver
    ```

2. **Access the Application:** 
   1. Open your web browser and navigate to the local server address: `http://127.0.0.1:8000/`
   2. To access the admin dashboard: `http://127.0.0.1:8000/admin/` and log in with the superuser credentials you created earlier.

You can now register a new user or log in with your superuser credentials to begin tracking vulnerabilities.

***

## Authors

Rifat Hossain

***

## Version History

* 0.1
    * Initial Release

***

## Acknowledgments

* [Django Documentation](https://docs.djangoproject.com/en/5.2/)
* [Django Tutorial](https://www.w3schools.com/django/index.php)
* [Bootstrap 5 (CSS framework for styling)](https://getbootstrap.com/)
* [SQLite (Database)](https://www.sqlite.org/index.html)
* [Google Gemini](https://gemini.google.com/share/40f29992bf64)