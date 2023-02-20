from flask import Blueprint, render_template

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/plants")
def go_to_plants():
    return render_template("plants.html")

@views.route("/diseases")
def go_to_diseases():
    return render_template("diseases.html")

@views.route("/aboutus")
def go_to_aboutus():
    return render_template("aboutus.html")