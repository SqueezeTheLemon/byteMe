from flask import Flask, render_template, request
import sys

application = Flask(__name__)

@application.route("/")
def hello():
    return render_template("index.html")

@application.route("/login")
def view_login():
    return render_template("login.html")

@application.route("/mypage")
def view_mypage():
    return render_template("mypage.html")

@application.route("/basket")
def view_basket():
    return render_template("basket.html")

@application.route("/customer_center")
def view_customer_center():
    return render_template("customer_center.html")

@application.route("/menu")
def view_list():
    return render_template("menu.html")

@application.route("/store")
def reg_review():
    return render_template("store.html")

@application.route("/review")
def view_review():
    return render_template("review.html")

@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@application.route("/submit_item")
def reg_item_submit():
    name=request.args.get("name")
    category=request.args.get("category")
    price=request.args.get("price")
    card=request.args.get("card")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    phone=request.args.get("phone")
    info=request.args.get("info")
    opt=request.args.get("opt")
    print(name,category,price,card,seller,addr,phone,info,opt)
    #return render_template("reg_item.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    return render_template("result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
