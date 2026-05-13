#!/usr/bin/python3
from flask import Flask, render_template, request, make_response, redirect
app = Flask(__name__)

@app.route('/')
def root():
    '''
    text = 'Hello User!'
    text = '<strong>' + text + '</strong>'
    return text
    '''
    messages = [{}]

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    print('good credentials=' , good_credentials)

    return render_template('route.html', logged_in=good_credentials, messages=messages)

def print_debug_info():
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))
    print('request.form.get("username")=', request.form.get("use    rname"))
    print('request.form.get("password")=', request.form.get("password"))
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))

def are_credentials_good(username, password):
    if username == 'haxor' and password == '1773':
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)
    good_credentials = are_crendentials_good(username,password)
    print('good_credentials=', good_credentials)
    if username is None:
        return render_template('login.html', bad_credentials=True)
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            template = return render_template('login.html', bad_credentials=False, logged_in=True)
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response


@app.route('/logout')
def logout():
    print_debug_info()
    return 'logout page'

app.run()
