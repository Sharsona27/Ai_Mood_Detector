from flask import Flask, render_template

# Initialize the Flask app
app = Flask(__name__)

# Routes for main pages
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/forget')
def forget():
    return render_template('forgot.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

if __name__ == '__main__':
    app.run(debug=True)
