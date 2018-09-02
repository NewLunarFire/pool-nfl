from flask import Flask, redirect, render_template, request, session, url_for
import locale

from db import close_connection
from sql import get_matches_for_week, save_picks, verify_user_password

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# TODO: Actually make this secret
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

locale.setlocale(locale.LC_ALL, 'fr_CA.utf8')

@app.teardown_appcontext
def teardown(exception):
    close_connection(exception)

@app.route("/")
def hello():
    if 'uid' in session:
        return redirect(url_for('week', week=1))
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    has_login_err = False

    if 'uid' in session:
        return redirect(url_for('week', week=1))

    if request.method == 'POST':
        uname = request.form.get("uname")
        uid = verify_user_password(uname, request.form.get("password"))
        if uid != None:
            session['uname'] = uname
            session['uid'] = uid
            return redirect(url_for('week', week=1))
        else:
            has_login_err = True
        
    
    return render_template('login.html', has_login_err=has_login_err)

@app.route("/week/<week>", methods=['GET', 'POST'])
def week(week):
    if request.method == 'POST':
        print(request.form)
        save_picks(request.form, session['uid'])
    
    return render_template('week.html', week=week, matches=get_matches_for_week(week, session['uid']))

@app.route("/logout")
def logout():
    session.pop('uid')
    return redirect(url_for('login'))
