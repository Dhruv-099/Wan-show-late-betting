from flask import Flask
from Website import create_app  
from Website.views import views 

app = create_app()
app.config['DEBUG'] = False  

if 'views' not in app.blueprints:  
    app.register_blueprint(views, url_prefix="/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)