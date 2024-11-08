from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import sys
import hashlib

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler

application.config['TEMPLATES_AUTO_RELOAD'] = True


@application.route("/", methods=["GET", "POST"])
def hello():
    return render_template("index.html")

@application.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@application.route("/login_selection")
def login_selection():
    return render_template("login_selection.html")

@application.route("/user_login", methods=["GET", "POST"])
def user_login():
     if request.method == "POST":
        # 로그인 인증 로직 (예: 사용자 이름과 비밀번호 확인)
        # 인증 성공 시 홈으로 리디렉션
        return redirect(url_for('home'))
     return render_template("user_login.html")
   

@application.route("/admin_login",methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template("admin_login.html")


@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("user_login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")


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

@application.route("/drink")
def view_drink():
    return render_template("drink.html")

@application.route("/dessert")
def view_dessert():
    return render_template("dessert.html")

@application.route("/gimbap")
def view_gimbap():
    return render_template("gimbap.html")

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
    payment=request.args.getlist("payment")
    stock=request.args.get("stock")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    phone=request.args.get("phone")
    info=request.args.get("info")
    opt=request.args.get("opt")
    print(name,category,price,payment,seller,addr,phone,info,opt)
    #return render_template("reg_item.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    payment=data.getlist("payment")
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("result.html", data=data, payment=payment, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
