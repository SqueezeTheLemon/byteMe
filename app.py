from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sys
import math

from werkzeug.utils import secure_filename
import os
from flask import get_flashed_messages
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
        id_ = request.form.get('id')
        pw = request.form.get('pw')
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        if DB.find_user(id_, pw_hash):
            position = DB.get_position(id_)
            if position == "user":  # 일반 사용자만 로그인 허용
                session['id'] = id_
                return render_template("home.html")
            else:
                flash("관리자 계정으로는 일반 사용자 페이지에 로그인할 수 없습니다!")
                return render_template("user_login.html")
        else:
            flash("Wrong ID or PW!")
            return render_template("user_login.html")

    return render_template("user_login.html")  # GET 요청 처리

@application.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        id_ = request.form.get('id')
        pw = request.form.get('pw')
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        if DB.find_user(id_, pw_hash):
            position = DB.get_position(id_)
            if position == "admin":  # 관리자만 로그인 허용
                session['id'] = id_
                session['position'] = position  # position 정보 추가
                return render_template("home.html")
            else:
                flash("일반 사용자 계정으로는 관리자 페이지에 로그인할 수 없습니다!")
                return render_template("admin_login.html")
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

# 회원가입
@application.route("/signup_post", methods=['POST'])
def register_user():
    # 구매 횟수 초기화
    num = 0
    data = {
        "id": request.form.get("id"),
        "pw": request.form.get("pw"),
        "email": request.form.get("email"),
        "name": request.form.get("name"),
        "nickname": request.form.get("nickname"),
        "position": request.form.get("position"),
        "phone": request.form.get("phone"),
        # 구매 횟수
        "num": num
    }
    pw_confirm = request.form.get("pw_confirm")

    if data["pw"] != pw_confirm:
        return redirect(url_for("signup", message="password_mismatch"))

    # 비밀번호 해싱
    pw_hash = hashlib.sha256(data["pw"].encode('utf-8')).hexdigest()

    # 비밀번호를 해싱된 값으로 대체
    data["pw"] = pw_hash


    if DB.insert_user(data, pw=pw_hash):
        return redirect(url_for("signup", message="success"))
    else:
        return redirect(url_for("signup", message="user_exists"))

# 마이페이지
@application.route("/mypage")
def view_mypage():
    if 'id' not in session:  
        flash("로그인이 필요합니다!")
        session.modified = True
        return redirect(url_for("login_selection"))
    
    # Flash 메시지 디버깅
    if "_flashes" in session:
        print("Flash 메시지 확인:", session["_flashes"])  # 세션 내 Flash 메시지 확인
    
    user_id=session["id"]
    
    # 일반회원인지 관리자인지 확인
    position = DB.get_position(user_id)

    # 닉네임 반환
    nickname = DB.get_nickname(user_id)

    # 관리자일 때
    if position == "admin":
        item = DB.get_no_complete()
        tot_count = len(item)
        data=DB.get_items()
        new_complete=DB.count_complete()
        return render_template("mypage_manager.html", items=item, total=tot_count, datas=data.items(), complete=new_complete, nickname=nickname)
    # 일반회원일 때
    else:
        if position == "user":
            item = DB.find_purchase(user_id)
            if item != []:
                total=1
            else:
                total=0
            data=DB.get_items()
            # 구매 횟수
            num = DB.get_num(user_id)
            return render_template("mypage_user.html", item=item, total=total, datas=data.items(), num=num, nickname=nickname)  

@application.route("/customer_center")
def view_customer_center():
    return render_template("customer_center.html")

@application.route("/menu")
def view_list():
    page = request.args.get("page", 0, type=int)  # 페이지 번호 가져오기
    category = request.args.get("category", "All")
    per_page = 4  # 한 페이지에 보여줄 아이템 수
    per_row = 4  # 한 행에 보여줄 아이템 수(1*4)
    row_count = int(per_page / per_row)  # 전체 행 수
    start_idx = per_page * page  # 시작 인덱스
    end_idx = per_page * (page + 1)  # 끝 인덱스

    # 카테고리별 아이템 가져오기
    #data = DB.get_items_bycategory(category)  # 카테고리에 맞는 데이터 가져오기
    if category=="All":
        data = DB.get_items() #read the table
    else:
        data = DB.get_items_bycategory(category)
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False))
    item_counts = len(data)
    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
        data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)  # 페이지네이션 후 데이터의 총 개수
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    # 템플릿 렌더링
    return render_template(
        "menu.html", 
        data=data.items(), 
        row1=locals()['data_0'].items(),
        limit=per_page,
        page=page,
        page_count=int(math.ceil(item_counts/per_page)),  # 총 페이지 수 계산
        total=item_counts,
        category=category #카테고리 html코드로 넘겨줌
        )
    


# @application.route("/drink")
# def view_drink():
#     # 특정 카테고리 데이터를 가져옴
#     items = DB.get_items_bycategory("음료")
#     return render_template("drink.html")

# @application.route("/dessert")
# def view_dessert():
#     return render_template("dessert.html")

# @application.route("/gimbap")
# def view_gimbap():
#     return render_template("gimbap.html")

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
    print(name,category,price,payment,stock,seller,addr,phone,info,opt)
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

@application.route("/product_edit")
def product_edit():
    nickname = DB.get_nickname(session["id"])
    return render_template("product_edit.html", nickname=nickname)

# 상품 정보 수정
@application.route("/edit_item_post", methods=['POST'])
def edit_item_post():
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
    updated_data = request.form.to_dict()
    updated_data['payment'] = request.form.getlist("payment")  # 결제 수단을 리스트로 저장

    # 데이터베이스에서 사용자 정보 업데이트
    if DB.update_item(updated_data, filename):
        flash("상품 정보가 수정되었습니다.")
        # 템플릿에 데이터 전달
        return render_template("result.html", data=updated_data, payment=updated_data['payment'], img_path=img_path)
    else:
        flash("상품 정보 수정에 실패했습니다.")
        return redirect(url_for("product_edit"))
    
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

    average_rating = DB.get_average_rating(name)
    return render_template("detail.html", name=name, data=data,
                           average_rating=average_rating if average_rating is not None else "No ratings yet")

@application.route("/submit_review_post", methods=['POST'])
def reg_review_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    return render_template("review_card.html", data=data, img_path="static/images/{}".format(image_file.filename))

# 여행 화면
@application.route('/travel')
def travel():
    if 'id' not in session:  # 세션에 로그인 정보가 없으면
        flash("로그인이 필요합니다!") 
        return redirect(url_for("login_selection"))
    
    # 구매 횟수
    num = DB.get_num(session["id"])

    return render_template("travel.html", num=num) 

# 주문 내역 페이지
@application.route("/my-order-history")
def my_order_history():
    user_id=session["id"]
    item = DB.find_purchase(user_id)
    if item != []:
          total=1
    else:
        total=0
    data=DB.get_items()
    # 구매 횟수
    num = DB.get_num(user_id)
    nickname = DB.get_nickname(user_id)
    return render_template("my-order-history.html", item=item, total=total, datas=data.items(), num=num, nickname=nickname)

# 구매 내역 페이지
@application.route("/my-ordered")
def my_ordered():
    user_id=session["id"]
    item = DB.find_buy(user_id)
    if item != []:
          total=1
    else:
        total=0
    data=DB.get_items()
    # 구매 횟수
    num = DB.get_num(user_id)
    nickname = DB.get_nickname(user_id)
    return render_template("my-ordered.html", item=item, total=total, datas=data.items(), num=num, nickname=nickname)

# 좋아요 페이지
@application.route("/liked_page")
def liked_page():
    num = DB.get_num(session['id'])
    nickname = DB.get_nickname(session['id'])
    return render_template("liked_page.html", num=num, nickname=nickname)

# 나의 리뷰 페이지
@application.route("/my-review")
def my_review():
    user_id=session["id"]
    review = DB.find_review(user_id)
    num = DB.get_num(user_id)
    nickname = DB.get_nickname(user_id)
    return render_template("my-review.html", num=num, nickname=nickname, review=review)

# 공감 리뷰 페이지
@application.route("/liked-review")
def liked_review():
    num = DB.get_num(session['id'])
    nickname = DB.get_nickname(session['id'])
    return render_template("liked-review.html", num=num, nickname=nickname)

# 계정 정보 수정 페이지 (일반회원, 관리자 공통)
@application.route("/edit_account", methods=["POST"])
def edit_account():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user_login"))

    user_id = session["id"]

    # 수정할 데이터 받기
    updated_data = {
        "nickname": request.form.get("nickname"),
        "email": request.form.get("email"),
        "name": request.form.get("name"),
        "position": request.form.get("position"),
        "phone": request.form.get("phone"),
    }

    # 데이터베이스에서 사용자 정보 업데이트
    if DB.update_user(user_id, updated_data):
        flash("정보가 수정되었습니다.")
        return redirect(url_for("view_mypage"))
    else:
        flash("정보 수정에 실패했습니다.")
        return redirect(url_for("edit_member_info"))
    

# 계정 삭제 (일반회원, 관리자 공통)
@application.route("/delete_account", methods=["POST"])
def delete_account():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user_login"))
    
    user_id = session["id"]

    # 데이터베이스에서 사용자 삭제
    DB.delete_user(user_id)
    
    # 세션 종료
    session.clear()
    flash("계정이 삭제되었습니다.")

    return redirect(url_for("home"))

@application.route("/edit-info", methods=["GET"])
def edit_member_info():
    nickname = DB.get_nickname(session["id"])
    # edit-info.html 페이지 렌더링
    return render_template("edit-info.html", nickname=nickname)


########################################################

# 주문 내역 페이지
@application.route("/order-history")
def order_history():
    item = DB.get_no_complete()
    tot_count = len(item)
    data=DB.get_items()
    new_complete=DB.count_complete()
    nickname = DB.get_nickname(session["id"])
    return render_template("order-history.html", items=item, total=tot_count, datas=data.items(), complete=new_complete, nickname=nickname)

# 완료 내역 페이지
@application.route("/ordered")
def ordered():
    item = DB.find_complete()
    if item != []:
        total=1
    else:
        total=0
    data=DB.get_items()
    new_complete=DB.count_complete()
    tot_count=len(DB.get_no_complete())
    nickname = DB.get_nickname(session["id"])
    return render_template("ordered.html", items=item, total=tot_count, datas=data.items(), complete=new_complete, tot=total, nickname=nickname)  # templates/ordered.html

# 상품 구매
@application.route("/purchase_item", methods=["POST"])
def purchase_item():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("user_login"))

    user_id = session['id']
    item_name = request.form.get("item_name")
    # 구매 수량
    num_item = request.form.get("num_item")
    # 완료 여부 초기화
    status = "N"

    # 구매 내역 데이터 생성
    purchase_data = {
        "user_id": user_id,
        "item_name": item_name,
        # 구매 수량
        "num_item": num_item,
        # 완료 여부
        "status": status
    }

    # 구매 횟수 업데이트
    new_num=DB.count_num(user_id)
    DB.update_num(user_id, new_num)

    # 구매 정보 저장
    if DB.record_purchase(purchase_data):
        # 구매 성공 처리
        message = f"{item_name} 구매가 완료되었습니다!"
        return jsonify({"success": True, "message": message, "redirect_url": url_for("view_mypage")})
    else:
        # 실패 처리
        message = "구매 처리에 실패했습니다. 다시 시도해주세요."
        return jsonify({"success": False, "message": message})

# 처리 완료
@application.route("/complete_item", methods=["POST"])
def complete_item():
    user_id = request.form.get("user_id")
    item_name = request.form.get("item_name")

    # 완료 여부 업데이트
    DB.update_status(user_id, item_name)

    # 완료 횟수 업데이트
    new_complete=DB.count_complete()

    # 대기 주문 횟수 업데이트
    item = DB.get_no_complete()
    tot_count = len(item)

    data=DB.get_items()

    return render_template("mypage_manager.html", complete=new_complete, total=tot_count, items=item, datas=data.items())


#로그인 확인 
@application.route('/api/check-login')
def check_login():
    if 'id' in session:
        return jsonify({'is_logged_in': True})
    else:
        return jsonify({'is_logged_in': False})

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
