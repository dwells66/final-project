from flask import Flask, render_template, request, make_response, redirect

app = Flask(__name__)

@app.route('/')
def root():
    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)

    if good_credentials:
        return render_template('route.html')
    else:
        return render_template('login.html')

def are_credentials_good(username, password):
    if username == 'haxor' and password == '1773':
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if are_credentials_good(username, password):
            response = make_response(redirect('/'))
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response
        else:
            return render_template('login.html', bad_credentials=True)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    return response

if __name__ == '__main__':
    app.run()
