from db import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    kanjis = db.relationship('Kanji', backref='owner', lazy=True, cascade="all, delete-orphan")
    phrases = db.relationship('Phrase', backref='creator', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario {self.email}>"


