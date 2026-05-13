import os

import random

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response,
    redirect,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)

@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """

@app.route('/')
def root():
    page = request.args.get('page', 0, type=int)
    limit = 20
    offset = page * limit

    query = text("""
        SELECT
            u.screen_name AS username,
            t.id_users,
            t.created_at,
            t.text
        FROM tweets_clean t
        JOIN users_clean u on u.id_users = t.id_users
        ORDER BY t.created_at DESC
        LIMIT :limit
        OFFSET :offset;
    """)

    rows = db.session.execute(
        query,
        {"limit": limit, "offset": offset}
    ).fetchall()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    logged_in = are_credentials_good(username, password)

    return render_template(
        'route.html',
        logged_in=logged_in,
        tweets=rows,
        page=page
    )

def are_credentials_good(username, password):
    result = db.session.execute(
        text("""
            SELECT 1
            FROM credentials
            WHERE username = :username
            AND password_hash = :password
        """),
        {"username": username, "password": password}
    ).fetchone()

    return result is not None

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
            return render_template('login.html', bad_credentials=True, logged_in=False)
    else:
        return render_template('login.html', bad_credentials=False, logged_in=False)

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    return response

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))

    limit = 20
    offset = (page - 1) * limit

    username = request.cookies.get("username")
    password = request.cookies.get("password")

    logged_in = are_credentials_good(username, password)


    if not query:
        return render_template("search.html", results=[], query="", page=page, logged_in=logged_in)

    sql = text("""
        WITH q AS (
            SELECT plainto_tsquery('english', :query) AS ts_query
        )
        SELECT
            t.id_users AS username,
            t.text,
            t.created_at,

            to_tsvector('english', t.text) <=> q.ts_query AS distance,

            ts_headline(
                'english',
                t.text,
                q.ts_query,
                'StartSel=<mark>, StopSel=</mark>'
            ) AS highlighted_text

        FROM tweets_clean t,
        q

        WHERE to_tsvector('english', t.text) @@ q.ts_query

        ORDER BY
            distance ASC,
            t.created_at DESC

        LIMIT :limit OFFSET :offset;
    """)

    results = db.session.execute(sql, {
        "query": query,
        "limit": limit,
        "offset": offset
    }).fetchall()

    return render_template(
        "search.html",
        results=results,
        query=query,
        page=page,
        logged_in=logged_in
    )

@app.route("/create_account", methods=["GET", "POST"])
def create_account():

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            return render_template("create_account.html", error="Passwords do not match")

        try:
            # 1. check if user exists
            exists = db.session.execute(text("""
                SELECT 1 FROM credentials
                WHERE username = :u
            """), {"u": username}).fetchone()

            if exists:
                return render_template("create_account.html", error="User already exists")

            db.session.execute(
                text("""
                    LOCK TABLE users_clean IN EXCLUSIVE MODE;
                """)
            )

            # generate new id safely (within lock)
            new_id = db.session.execute(
                text("""
                    SELECT COALESCE(MAX(id_users), 0) + 1
                    FROM users_clean
                """)
            ).scalar()

            # insert into users_clean first
            db.session.execute(
                text("""
                    INSERT INTO users_clean (
                        id_users,
                        screen_name,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :id,
                        :username,
                        NOW(),
                        NOW()
                    )
                """),
                {
                    "id": new_id,
                    "username": username
                }
            )

            # insert into credentials
            db.session.execute(
                text("""
                    INSERT INTO credentials (
                        id_users,
                        username,
                        name,
                        password_hash
                    )
                    VALUES (
                        :id,
                        :username,
                        :name,
                        :password
                    )
                """),
                {
                    "id": new_id,
                    "username": username,
                    "name": name,
                    "password": password1
                }
            )
            # 5. commit both
            db.session.commit()

            return redirect("/login")

        except:
            db.session.rollback()
            return render_template("create_account.html", error="Error creating account")

    return render_template("create_account.html")

@app.route("/create_message", methods=["GET", "POST"])
def create_message():

    username = request.cookies.get("username")

    if not username:
        return redirect("/login")

    logged_in = are_credentials_good(
        request.cookies.get("username"),
        request.cookies.get("password")
    )

    if request.method == "POST":

        message = request.form.get("message")

        if not message:
            return render_template(
                "create_message.html",
                error="Message cannot be empty", logged_in=logged_in
            )

        try:
            # get user id
            user = db.session.execute(
                text("""
                    SELECT id_users
                    FROM credentials
                    WHERE username = :u
                """),
                {"u": username}
            ).fetchone()

            if not user:
                return redirect("/login")

            user_id = user[0]

            # 🔒 LOCK tweets table to prevent duplicate MAX(id)+1
            db.session.execute(
                text("""
                    LOCK TABLE tweets_clean IN EXCLUSIVE MODE;
                """)
            )

            # generate new tweet id safely
            new_tweet_id = db.session.execute(
                text("""
                    SELECT COALESCE(MAX(id_tweets), 0) + 1
                    FROM tweets_clean
                """)
            ).scalar()

            # insert tweet
            db.session.execute(
                text("""
                    INSERT INTO tweets_clean (
                        id_tweets,
                        id_users,
                        text,
                        created_at
                    )
                    VALUES (
                        :id_tweets,
                        :id_users,
                        :text,
                        NOW()
                    )
                """),
                {
                    "id_tweets": new_tweet_id,
                    "id_users": user_id,
                    "text": message
                }
            )

            db.session.commit()
            return redirect("/")

        except Exception:
            db.session.rollback()
            return render_template(
                "create_message.html",
                error="Error creating message", logged_in=logged_in
            )

    return render_template("create_message.html", logged_in=logged_in)
if __name__ == '__main__':
    app.run()
