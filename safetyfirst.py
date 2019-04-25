import sqlite3 as sql
from random import randint
from flask import g
from flask import Flask, redirect, request, jsonify, make_response, render_template
from flask_qrcode import QRcode
import authorization_code_grant
from authorization_code_grant import get_api_client
from authorization_code_grant import hello_user

app = Flask(__name__)

QRcode(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/start/')
def my_page():
  return render_template('start.html', auth_url=authorization_code_grant.auth_url)

@app.route('/qr/<lyft_id>/')
def show_qr_code(lyft_id):
  q = 'SELECT lyft_id FROM lyfters WHERE lyft_id=?'
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute(q, (lyft_id,))
    lyfter = cur.fetchone()
  if lyfter is not None:
    return render_template('qr.html', lyft_id=lyfter[0])
  else:
    return redirect('/')

@app.route('/complete/', methods=['GET'])
def oauth_complete():
  if not (request.args.get('code') and request.args.get('state')):
    print('no code or state to get')
    return redirect('/')

  try:
    api_client = get_api_client(request.url)
    user_data = hello_user(api_client)
  except:
    print('api client user data wrong')
    return redirect('/')

  with sql.connect("database.db") as con:
    cur = con.cursor()
    try:
      cur.execute("INSERT INTO lyfters (first_name,last_name,lyft_id) VALUES (?,?,?)",(user_data.get('first_name'),user_data.get('last_name'),user_data.get('id')))
    # except sql.IntegrityError:
      # print('integrity error')
    except:
      return redirect('/')
  return render_template('qr.html', lyft_id=user_data.get('id'))

@app.route('/verify/')
def verify_qr():
  return render_template('verify_qr.html')

"""
- Redirect user to lyft login, get oauth creds
- get lyft id, if exists, store oauth session and ids
- create qr code, save to row
Each Row Has:
UUID, Lyft_ID, firstname, lastname, vehicle, v_img, /
driver_img, oauth_session_creds..., qr_code, first_safety_check
"""

if __name__ == '__main__':
  app.run(debug=True)
