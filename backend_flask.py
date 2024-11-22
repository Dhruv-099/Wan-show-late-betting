from flask import Flask
from Website import create_app  
from Website.views import views 

# Create the Flask application
app = create_app()
app.config['DEBUG'] = False  # Set DEBUG mode to False for production

# Register the views blueprint if not already registered
if 'views' not in app.blueprints:  
    app.register_blueprint(views, url_prefix="/")

# Run the application if this script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)