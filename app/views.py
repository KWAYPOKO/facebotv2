import datos
import json
from flask import (
  Blueprint,
  render_template,
  request,
  redirect,
  url_for,
  session
)

config = json.load(open('config.json', 'r'))
view = Blueprint('view',__name__)

@view.route('/')
@view.route('/home')
def root():
  example = {
    "name": "FBBOT",
    "owner": "Unknown",
    "admins": ["Andrei Dsoyo."],
    "commands": ["help", "uid", "shoti", "kick", "admins", "hack"],
    "events": ["joinNoti.py", "walalang.py"]
  }
  return render_template('home.html',
    title="Facebot | home",
    show_eruda=True,
    bot=example
  ),200

# Admin
@view.route('/admin/log')
def admin_log():
  return render_template('admin/log.html', session=datos.log_session, show_eruda=True), 200

@view.route('/admin/login', methods=['GET','POST'])
def admin_login():
  error = None
  password = 'admin123'
  if config.get('website'):
    pass_ = config['website'].get('admin_password')
    if pass_:
      password = pass_
  
  if request.method == 'POST':
    get_password = request.form.get('password')
    if get_password == password:
      error = None
      return redirect(url_for('view.root'))
    else:
      error = "Invalid password"
  return render_template('admin/login.html', title='Admin login', error=error), 200