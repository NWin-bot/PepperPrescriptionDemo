from flask import Blueprint, render_template, request
import os

views = Blueprint(__name__, "views")

@views.route("/", methods=["POST","GET"])
def home():
    if request.method=='POST':
        f=request.files["image"]
        filename=f.filename
        Path=os.path.join("static/uploads",filename)
        f.save(Path)
        return render_template('index.html',upload_hold=True,img_name=filename)
    return render_template('index.html',upload_hold=False,img_name="")

@views.route("/plants")
def go_to_plants():
    return render_template("plants.html")

@views.route("/diseases")
def go_to_diseases():
    return render_template("diseases.html")

@views.route("/aboutus")
def go_to_aboutus():
    return render_template("aboutus.html")