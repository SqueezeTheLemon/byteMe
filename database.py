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
            "phone": data['phone']
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
