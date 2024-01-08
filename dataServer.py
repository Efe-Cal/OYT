from json import load
from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user
from face_recognition_methods import load_faces

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user credentials
PASSWORD = '1234'

# User class for Flask-Login
class User(UserMixin):
    pass

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # In this example, we only have one user
        user = User()
        user.id = user_id
        return user

@app.route('/login/<password>', methods=['GET'])
def login(password):
    if str(password) == PASSWORD:
        user = User()
        user.id = 1
        login_user(user)  # Login the user
        return 'Login successful!'
    else:
        return 'Invalid password'

@app.route('/getFaceEncodings/<sinif>')
@login_required  # Protect the route
def protected(sinif):
    data = load_faces(sinif)
    data[0] = [i.tolist() for i in data[0]]
    return jsonify(data)

if __name__ == '__main__':
    app.run(port = 7777,debug=True)
