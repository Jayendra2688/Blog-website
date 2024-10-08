# Flask Blog Project

This project is a fully functional blog web application built using the Flask framework. It includes features such as user authentication, post creation, editing, and deletion (for admins), and a commenting system for registered users. The project also uses WTForms for form handling, SQLAlchemy for database management, and integrates several Flask extensions like CKEditor and Gravatar for enhanced functionality.

## Features

- **User Authentication**: Register, log in, and log out functionality using `Flask-Login`.
- **Admin Functionality**: Admin users can create, edit, and delete blog posts.
- **Commenting System**: Registered users can comment on blog posts.
- **Rich Text Editor**: Blog posts use `Flask-CKEditor` to allow for rich text formatting.
- **Gravatar Integration**: User profile images are pulled from Gravatar using the `Flask-Gravatar` extension.

## Technologies Used

- **Flask**: A micro web framework for Python.
- **SQLAlchemy**: An ORM (Object Relational Mapper) for database interactions.
- **WTForms**: For creating and validating forms.
- **Flask-Login**: For user session management and authentication.
- **Flask-Bootstrap**: For adding Bootstrap components to the UI.
- **Flask-CKEditor**: For rich-text blog post editing.
- **Flask-Gravatar**: For user avatars via Gravatar.
- **Werkzeug**: For password hashing and security.
  
## Project Structure

```plaintext
├── app.py                  # Main Flask application
├── forms.py                # WTForms for handling forms
├── templates/
│   ├── base.html           # Base template for the app
│   ├── index.html          # Home page showing all posts
│   ├── login.html          # User login page
│   ├── register.html       # User registration page
│   ├── make-post.html      # Form for creating/editing posts
│   ├── post.html           # Detailed view of a single blog post
│   └── ...                 # Other HTML templates
├── static/
│   ├── style.css           # Custom stylesheets
├── posts.db                # SQLite database
├── README.md               # Project documentation
└── requirements.txt        # Project dependencies
