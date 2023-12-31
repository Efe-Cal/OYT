from flask import Flask, render_template, url_for, request, redirect
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.secret_key=os.environ['SECRET_KEY'] if os.environ.get('SECRET_KEY') else os.urandom(24)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):

    user = User()
    user.id = email
    return user

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        if request.form["pin"]==os.environ['PASSWORD']:
            print("login success")
            user = User()
            user.id = "admin"
            login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run("0.0.0.0",debug=True)