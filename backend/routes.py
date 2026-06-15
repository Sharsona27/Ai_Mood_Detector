from backend.mood_detector import detect_mood, detect_mood_from_image

from backend.combined_detector import predict_combined_emotion, detect_combined_emotion_from_image
from flask import Blueprint, send_file, render_template, request, redirect, session, flash, jsonify
from flask import redirect,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import get_connection
from datetime import datetime

main = Blueprint('main', __name__)


# ============= NEW API ENDPOINTS FOR BROWSER CAMERA =============

@main.route('/api/detect-mood', methods=['POST'])
def api_detect_mood():
    """
    API endpoint to detect mood from a single image.
    Expects JSON with 'image' key containing base64 encoded image data.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        
        # Detect mood from image
        result = detect_mood_from_image(image_data)
        
        # Save to database if mood was detected successfully
        if result.get('emotion') != 'Unknown':
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO mood_history (user_id, mood, timestamp) VALUES (?, ?, ?)',
                    (session['user_id'], result['emotion'], datetime.now())
                )
                conn.commit()
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                conn.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'emotion': 'Unknown'}), 500


@main.route('/api/detect-combined-emotion', methods=['POST'])
def api_detect_combined_emotion():
    """
    API endpoint to detect emotion using both custom model and DeepFace.
    Expects JSON with 'image' key containing base64 encoded image data.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        
        # Detect combined emotion from image
        result = detect_combined_emotion_from_image(image_data)
        
        # Save to database if emotion was detected successfully
        if result.get('emotion') != 'Unknown':
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO mood_history (user_id, mood, timestamp) VALUES (?, ?, ?)',
                    (session['user_id'], result['emotion'], datetime.now())
                )
                conn.commit()
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                conn.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'emotion': 'Unknown'}), 500


# ============= EXISTING ROUTES =============

@main.route('/')
def root():
    return render_template('home.html')








@main.route('/index')
def index():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('index.html')



@main.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('home.html')


# Register Page
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match!', 'danger')
        else:
            conn = get_connection()
            try:
                cursor = conn.cursor()
                hashed_pw = generate_password_hash(password)
                cursor.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashed_pw)
                )
                conn.commit()
                flash('Registration successful!', 'success')
                return redirect('/login')
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                conn.close()

    return render_template('register.html')

# Login Page
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login successful!', 'success')
                return redirect(url_for('main.index')) 
            else:
                flash('Invalid credentials!', 'danger')
        finally:
            conn.close()

    return render_template('login.html')



@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # TODO: integrate email delivery for password reset link
        flash('If the email is registered, password reset instructions have been sent.')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html')


# Contact and Feedback Routes
@main.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    # Process/store the message
    flash('Message sent successfully!', 'success')
    return redirect(url_for('main.contact'))


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/contact')
def contact():
    return render_template('contact.html')


@main.route('/feedback', methods=['GET'])
def feedback():
    return render_template('feedback.html')

@main.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # process feedback logic here (e.g., save to DB or send email)
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    # Store or log this data
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('main.feedback'))


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.root'))  # instead of main.login


@main.route('/user-details')
def user_details():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('main.login'))

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
    finally:
        conn.close()

    return render_template('user_details.html', user=user)


@main.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    old_password = request.form['old_password']
    new_password = request.form['new_password']

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], old_password):
            hashed_new = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_new, session['user_id']))
            conn.commit()
            flash('Password changed successfully!', 'success')
        else:
            flash('Old password incorrect.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('main.user_details'))


@main.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    new_username = request.form['username']
    new_email = request.form['email']

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                       (new_username, new_email, session['user_id']))
        conn.commit()
        session['username'] = new_username
        flash('Profile updated!', 'success')
    finally:
        conn.close()

    return redirect(url_for('main.user_details'))



@main.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please log in to view your mood history.', 'warning')
        return redirect(url_for('main.login'))

    # ✅ ADD THIS LINE
    print("👉 Logged-in User ID:", session['user_id'])

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT mood, timestamp FROM mood_history WHERE user_id = ? ORDER BY timestamp DESC',
            (session['user_id'],)
        )
        history = cursor.fetchall()
    finally:
        conn.close()

    return render_template('history.html', history=history)


@main.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@main.route('/real-time-emotion')
def real_time_emotion():
    return render_template('real_time_emotion.html')

@main.route('/why-it-matters')
def why_it_matters():
    return render_template('why_it_matters.html')
