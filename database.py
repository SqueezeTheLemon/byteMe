import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database() 

    def insert_item(self, name, data, img_path):
    # payment 데이터를 문자열로 변환
        payment = data['payment']
        if isinstance(payment, list):
            payment = ",".join(payment)  # 리스트를 문자열로 변환

        item_info = {
            "name": data['name'],
            "price": data['price'],
            "category": data['category'],
            "payment": payment,  # 변환된 데이터를 저장
            "stock": data['stock'],
            "seller": data['seller'],
            "phone": data['phone'],
            "addr": data['addr'],
            "info": data['info'],
            "opt": data['opt'],
            "img_path": img_path
        }
        self.db.child("item").child(name).set(item_info)
        print("Inserted item:", item_info)
        return True

    def insert_user(self, data, pw):
        user_info ={
            "id": data['id'],
            "pw": pw,
            "nickname": data['nickname'],
            "email": data['email'],
            "name": data['name'],
            "position": data['position'],
            "phone": data['phone'],
            "num": data['num']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(user_info)
            return True
        else:
            return False

    def user_duplicate_check(self, id_string):
            users = self.db.child("user").get()
            print("users###",users.val())
            if str(users.val()) == "None": # first registration
                return True
            else:
                for res in users.each():
                    value = res.val()

                    if value['id'] == id_string:
                        return False
            return True
    
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value=res.val()

            if value['id']==id_ and value['pw']==pw_:
                return True #입력받은 아이디와 비밀번호의 해시값이 동일한 경우가 있는지 확인한다.
        return False
    
    def delete_user(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                self.db.child("user").child(res.key()).remove()
                print(f"Deleted user: {user_id}")
                return True
        return False

    def update_user(self, user_id, updated_data):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                self.db.child("user").child(res.key()).update(updated_data)
                print(f"Updated user: {user_id}")
                return True
        return False

    
    def get_items(self):
        items=self.db.child("item").get().val()
        return items
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value = ""
        print("###########", name)

        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()
                # payment가 문자열이라면 리스트로 변환
                if "payment" in target_value and isinstance(target_value['payment'], str):
                    target_value['payment'] = target_value['payment'].split(",")
        print("Retrieved item data:", target_value)
        return target_value
    
    # 상품 정보 수정
    def update_item(self, updated_data, img_path):
        payment = updated_data['payment']
        if isinstance(payment, list):
            payment = ",".join(payment)  # 리스트를 문자열로 변환
        
        items=self.db.child('item').get()
        for res in items.each():
            if res.key()==updated_data['name']:
                item_info = {
                    "price": updated_data['price'],
                    "category": updated_data['category'],
                    "payment": payment,  # 변환된 데이터를 저장
                    "stock": updated_data['stock'],
                    "seller": updated_data['seller'],
                    "phone": updated_data['phone'],
                    "addr": updated_data['addr'],
                    "info": updated_data['info'],
                    "opt": updated_data['opt'],
                    "img_path": img_path
                }
                self.db.child("item").child(res.key()).update(item_info)
                print("Inserted item:", item_info)
        return True

    def record_purchase(self, purchase_data):
        # "purchases" 경로에 데이터 저장
        self.db.child("purchases").push(purchase_data)
        print(f"Recorded purchase: {purchase_data}")
        return True
    
    # 구매 횟수 카운트
    def count_num(self, user_id):
        num = 0
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['user_id'] == user_id:
                num+=1
        print("Number of Purchases:", num)
        return num
    
    # 구매 횟수 업데이트
    def update_num(self, user_id, new_num):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                self.db.child("user").child(res.key()).update({"num": new_num})
                print("Update num")
                return True
        return False
    
    # 구매 횟수 반환
    def get_num(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                num=self.db.child("user").child(res.key()).child("num").get().val()
                if num == None:
                    new_num = self.count_num(user_id)
                    self.db.child("user").child(res.key()).update({"num": new_num})
                    return new_num
                return num
        return False
    
    # 직급 반환
    def get_position(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                position=self.db.child("user").child(res.key()).child("position").get().val()
                return position
        return False
    
    # 닉네임 반환
    def get_nickname(self, user_id):
        users = self.db.child("user").get()
        for res in users.each():
            if res.val()['id'] == user_id:
                nickname=self.db.child("user").child(res.key()).child("nickname").get().val()
                return nickname
        return False
    
    # 처리 중인 주문 튜플 (사용자 아이디, 상품명, 구매 수량) 형태로 반환
    def get_no_complete(self):
        items=[]
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['status'] == "N":
                if 'num_item' not in res.val():
                    res.val()['num_item'] = 1
                items.append((res.val()['user_id'], res.val()['item_name'], res.val()['num_item']))
        return items
    
    # 완료 여부 업데이트
    def update_status(self, user_id, item_name):
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['user_id'] == user_id and res.val()['status'] == "N" and res.val()['item_name'] == item_name:
                self.db.child("purchases").child(res.key()).update({"status": "Y"})
                print("Complete ", res.val()['item_name'], " : ", res.val()['user_id'])
                return True
        return False
    
    # 완료 횟수 카운트
    def count_complete(self):
        complete = 0
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['status'] == "Y":
                complete+=1
        print("Number of Complete:", complete)
        return complete
    
    # 주문 내역 확인
    def find_purchase(self, user_id):
        item=[]
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['user_id'] == user_id and res.val()['status'] == "N":
                if 'num_item' not in res.val():
                    res.val()['num_item'] = 1
                item.append((res.val()['item_name'], res.val()['num_item']))
        return item
    
    # 구매 내역 확인
    def find_buy(self, user_id):
        item=[]
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['user_id'] == user_id and res.val()['status'] == "Y":
                if 'num_item' not in res.val():
                    res.val()['num_item'] = 1
                item.append((res.val()['item_name'], res.val()['num_item']))
        return item
    
    # 완료 내역 확인
    def find_complete(self):
        item=[]
        purchases=self.db.child("purchases").get()
        for res in purchases.each():
            if res.val()['status'] == "Y":
                if 'num_item' not in res.val():
                    res.val()['num_item'] = 1
                item.append((res.val()['item_name'], res.val()['user_id'], res.val()['num_item']))
        return item