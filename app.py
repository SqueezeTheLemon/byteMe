from flask import Flask, render_template, request, redirect, url_for, jsonify
import sys
from werkzeug.utils import secure_filename
import os
application = Flask(__name__)

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
        username = request.form.get("username")
        password = request.form.get("password")
        # 로그인 인증 로직 (예: 사용자 이름과 비밀번호 확인)
        # 인증 성공 시 홈으로 리디렉션
        return redirect(url_for('home'))
     return render_template("user_login.html")
   

@application.route("/admin_login",methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template("admin_login.html")


@application.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template("signup.html")

#백엔드가 없어, 우선 user mypage에만 연결. 
@application.route("/mypage")
def view_mypage():
    return render_template("mypage_user.html")

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
def store():
    return render_template("store.html")

@application.route("/review_list")
def review_list():
    return render_template("review_list.html")

@application.route('/review_form')
def review_form():
    return render_template('review_form.html')

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


# static/images 폴더가 없을 경우 생성
os.makedirs("static/images", exist_ok=True)

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    # 이미지 파일 가져오기
    image_file = request.files.get("file")
    if image_file and image_file.filename:
        # 파일 이름을 안전하게 설정하고 경로 구성
        filename = secure_filename(image_file.filename)
        save_path = os.path.join("static", "images", filename)
        
        # 이미지 저장
        image_file.save(save_path)

        # img_path에 템플릿에서 접근 가능한 경로 설정
        img_path = url_for('static', filename=f'images/{filename}')
    else:
        # 이미지 파일이 없는 경우 기본 이미지 경로 설정
        img_path = url_for('static', filename='images/default_image.jpg')

    # 폼 데이터 처리
    data = request.form
    payment = data.getlist("payment")

    # 템플릿에 데이터 전달
    return render_template("result.html", data=data, payment=payment, img_path=img_path)

@application.route("/submit_review_post", methods=['POST'])
def reg_review_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    return render_template("review_card.html", data=data, img_path="static/images/{}".format(image_file.filename))


@application.route('/travel') 
def travel():
    return render_template("travel.html")  # 'travel.html'렌더링

@application.route('/api/order-count', methods=['GET'])
def get_order_count():
    order_count = 4 # 예시로 주문 횟수를 4로 설정
    return jsonify({'orderCount': order_count})


# 주문 내역 페이지
@application.route("/my-order-history")
def my_order_history():
    return render_template("my-order-history.html")

# 구매 내역 페이지
@application.route("/my-ordered")
def my_ordered():
    return render_template("my-ordered.html")

# 좋아요 페이지
@application.route("/like")
def like():
    return render_template("like.html")

# 나의 리뷰 페이지
@application.route("/my-review")
def my_review():
    return render_template("my-review.html")

# 공감 리뷰 페이지
@application.route("/liked-review")
def liked_review():
    return render_template("liked-review.html")

# 회원 정보 수정 페이지
@application.route("/edit-member-info")
def edit_member_info():
    return render_template("edit-member-info.html")

# 회원 탈퇴 페이지
@application.route("/delete-member")
def delete_member():
    return render_template("delete-member.html")

########################################################
# 상품 관리 페이지
@application.route("/product-manage")
def product_manage():
    return render_template("product-manage.html")

# 상품 수정 페이지
@application.route("/product-edit")
def product_edit():
    return render_template("product-edit.html")

# 재고 현황 페이지
@application.route("/product-stock")
def product_stock():
    return render_template("product-stock.html")

# 매니저 회원 정보 수정 페이지
@application.route("/edit-manager-info")
def edit_manager_info():
    return render_template("edit-manager-info.html")  # templates/edit_manager_info.html

# 매니저 회원 탈퇴 페이지
@application.route("/delete-manager")
def delete_manager():
    return render_template("delete-manager.html")  # templates/delete_manager.html

# 주문 내역 페이지
@application.route("/order-history")
def order_history():
    return render_template("order-history.html")  # templates/order_history.html

# 완료 내역 페이지
@application.route("/ordered")
def ordered():
    return render_template("ordered.html")  # templates/ordered.html



if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)

