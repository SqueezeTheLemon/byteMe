from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sys

from werkzeug.utils import secure_filename
import os

from database import DBhandler
import hashlib
import sys

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB=DBhandler()

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
        id_ = request.form.get('id')  # 안전하게 값을 가져옴
        pw = request.form.get('pw')
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        if DB.find_user(id_, pw_hash):  # 데이터베이스 조회
            session['id'] = id_
            return render_template("home.html")
        else:
            flash("Wrong ID or PW!")
            return render_template("user_login.html")

    return render_template("user_login.html")  # GET 요청 처리

     
   
@application.route("/admin_login",methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        id_ = request.form.get('id')  # 안전하게 값을 가져옴
        pw = request.form.get('pw')
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        if DB.find_user(id_, pw_hash):  # 데이터베이스 조회
            session['id'] = id_
            return render_template("home.html")
        else:
            flash("Wrong ID or PW!")
            return render_template("admin_login.html")

    return render_template("admin_login.html")  # GET 요청 처리

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('home'))

@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data = {
        "id": request.form.get("id"),
        "pw": request.form.get("pw"),
        "email": request.form.get("email"),
        "name": request.form.get("name"),
        "nickname": request.form.get("nickname"),
        "position": request.form.get("position"),
        "phone": request.form.get("phone")
    }
    pw_confirm = request.form.get("pw_confirm")

    if data["pw"] != pw_confirm:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for("signup"))

    # 비밀번호 해싱
    pw_hash = hashlib.sha256(data["pw"].encode('utf-8')).hexdigest()

    # 비밀번호를 해싱된 값으로 대체
    data["pw"] = pw_hash


    if DB.insert_user(data, pw=pw_hash):
        return redirect(url_for("user_login"))
    else:
        flash("user id already exist!")
        return redirect(url_for("signup"))

#백엔드가 없어, 우선 user mypage에만 연결. 
@application.route("/mypage")
def view_mypage():
    return render_template("mypage_user.html")

@application.route("/customer_center")
def view_customer_center():
    return render_template("customer_center.html")

@application.route("/menu")
def view_list():
    page=request.args.get("page", 0, type=int)
    per_page=4
    per_row=2
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data=DB.get_items() #read the table
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count=len(data)

    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("menu.html", data=data.items(), row1=locals()['data_0'].items(),
 row2=locals()['data_1'].items(), limit=per_page,
page=page,
page_count=int((item_counts/per_page)+1),
total=item_counts)

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


@application.route("/reg_review")
def reg_review():
    return render_template("reg_reviews.html")

@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("reg_reviews.html", name=name)

@application.route("/reg_review", methods=['POST'])
def reg_review_post():
    data=request.form
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    print(data)
    DB.reg_review(data, image_file.filename)
    return redirect(url_for('view_review'))

@application.route("/review_list")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=3# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table
    if data is None: 
        data = {}
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
        "review.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)


@application.route("/view_review_detail/<title>/")
def view_review_detail(title):
    print("###title:",title)
    data = DB.get_review_byname(str(title))
    print("####data:",data)
    return render_template("Review_detail.html", title=title, data=data)


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
    data = request.form.to_dict()
    data['payment'] = request.form.getlist("payment")  # 결제 수단을 리스트로 저장

    # DB에 데이터 저장
    DB.insert_item(data['name'], data, filename)

    # 템플릿에 데이터 전달
    return render_template("result.html", data=data, payment=data['payment'], img_path=img_path)


@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name)
    print("myheart", my_heart)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '좋아요 취소 완료!'})


@application.route('/dynamicurl/<varible_name>/')
def DynamicUrl(varible_name):
    return str(varible_name)

@application.route('/view_detail/<name>/')
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("detail.html", name=name, data=data)

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
@application.route("/liked_page")
def liked_page():
    return render_template("liked_page.html")

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
