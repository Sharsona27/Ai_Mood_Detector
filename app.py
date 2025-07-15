from flask import Flask
from backend.routes import main  # import the Blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session and flash

# Register Blueprint which handles:
# '/', '/home', '/demo', '/register', '/login'
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
