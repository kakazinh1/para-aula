from db import db

class Kanji(db.Model):
    __tablename__ = 'kanji'
    id = db.Column(db.Integer, primary_key=True)
    character = db.Column(db.String(10), unique=False, nullable=False)
    onyomi = db.Column(db.String(100), nullable=True)
    kunyomi = db.Column(db.String(100), nullable=True)
    meaning = db.Column(db.String(255), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    phrases = db.relationship('Phrase', backref='kanji', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Kanji {self.character} - {self.meaning}>"

class Phrase(db.Model):
    __tablename__ = 'phrase'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    
    kanji_id = db.Column(db.Integer, db.ForeignKey('kanji.id'), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f"<Phrase {self.text}>"