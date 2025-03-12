from flask_login import UserMixin

class User(UserMixin):                                                  #funzione che uso in app.py
    def __init__(self, id, email, nickname, password, immagine_profilo, creatore):
        self.id = id
        self.email= email     
        self.nickname = nickname
        self.password = password
        self.immagine_profilo = immagine_profilo
        self.creatore = creatore