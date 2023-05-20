from flask import Blueprint, render_template


main_blp = Blueprint("view", __name__, template_folder='templates', static_folder='static')

@main_blp.route("/")
def home_page():
    return render_template("index.html")

@main_blp.route("/index.html")
def index():
    return ('OK', 200)
