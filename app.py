import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db
from usuario import Usuario
from models import Kanji, Phrase
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db_path_from_env = os.getenv('DB_PATH')
if db_path_from_env is None:
    db_path_from_env = 'dbase/db.sqlite3' 
caminho_db = os.path.join(os.path.abspath(os.path.dirname(__file__)), db_path_from_env)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{caminho_db}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form['emailForm']
        senha = request.form['senhaForm']
        novo_usuario = Usuario(email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailForm']
        senha = request.form['senhaForm']
        user = Usuario.query.filter_by(email=email, senha=senha).first()
        session['user_id'] = user.id
        return redirect(url_for('kanji_list'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/pnginicial')
def pnginicial():
    if 'user_id' in session:
        return redirect(url_for('kanji_list'))
    else:
        return redirect(url_for('login'))

@app.route('/kanji')
def kanji_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    kanjis = Kanji.query.filter_by(user_id=user_id).all()
    print(f"DEBUG: Kanjis recuperados para user_id {user_id}: {kanjis}")
    return render_template('kanji_list.html', kanjis=kanjis)

@app.route('/kanji/add', methods=['GET', 'POST'])
def add_kanji():
    print("DEBUG: Entrou na rota add_kanji")
    if 'user_id' not in session:
        flash('Você precisa estar logado para adicionar Kanji.', 'warning')
        print("DEBUG: Usuário não logado, redirecionando para login.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        print("DEBUG: Método da requisição é POST.")
        character = request.form.get('character', '').strip()
        onyomi = request.form.get('onyomi', '').strip()
        kunyomi = request.form.get('kunyomi', '').strip()
        meaning = request.form.get('meaning', '').strip()
        user_id = session['user_id']

        print(f"DEBUG: Dados do formulário - Character: '{character}', Meaning: '{meaning}', Onyomi: '{onyomi}', Kunyomi: '{kunyomi}'")

        if not character or not meaning:
            flash('Caractere e significado são campos obrigatórios.', 'danger')
            print("DEBUG: Validação falhou: campos obrigatórios vazios.")
            return render_template('kanji_form.html', kanji=None)

        try:
            new_kanji = Kanji(character=character, onyomi=onyomi, kunyomi=kunyomi, meaning=meaning, user_id=user_id)
            db.session.add(new_kanji)
            db.session.commit()
            flash('Kanji adicionado com sucesso!', 'success')
            print(f"DEBUG: Kanji '{character}' adicionado com sucesso!")
            return redirect(url_for('kanji_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar Kanji: {e}', 'danger')
            print(f"DEBUG: ERRO ao adicionar Kanji: {e}")
            return render_template('kanji_form.html', kanji=None)

    print("DEBUG: Método da requisição é GET, renderizando formulário.")
    return render_template('kanji_form.html', kanji=None)

@app.route('/kanji/edit/<int:kanji_id>', methods=['GET', 'POST'])
def edit_kanji(kanji_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para editar Kanji.', 'warning')
        return redirect(url_for('login'))

    kanji = Kanji.query.filter_by(id=kanji_id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        kanji.character = request.form.get('character', '').strip()
        kanji.onyomi = request.form.get('onyomi', '').strip()
        kanji.kunyomi = request.form.get('kunyomi', '').strip()
        kanji.meaning = request.form.get('meaning', '').strip()

        if not kanji.character or not kanji.meaning:
            flash('Caractere e significado são campos obrigatórios.', 'danger')
            return render_template('kanji_form.html', kanji=kanji)

        try:
            db.session.commit()
            flash('Kanji atualizado com sucesso!', 'success')
            return redirect(url_for('kanji_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar Kanji: {e}', 'danger')
            return render_template('kanji_form.html', kanji=kanji)

    return render_template('kanji_form.html', kanji=kanji)

@app.route('/kanji/delete/<int:kanji_id>', methods=['POST'])
def delete_kanji(kanji_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para deletar Kanji.', 'warning')
        return redirect(url_for('login'))

    kanji = Kanji.query.filter_by(id=kanji_id, user_id=session['user_id']).first_or_404()
    try:
        db.session.delete(kanji)
        db.session.commit()
        flash('Kanji deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar Kanji: {e}', 'danger')
    return redirect(url_for('kanji_list'))

@app.route('/kanji/<int:kanji_id>/phrases')
def phrase_list(kanji_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para ver frases.', 'warning')
        return redirect(url_for('login'))

    kanji = Kanji.query.filter_by(id=kanji_id, user_id=session['user_id']).first_or_404()
    phrases = Phrase.query.filter_by(kanji_id=kanji_id, user_id=session['user_id']).all()
    return render_template('phrase_list.html', kanji=kanji, phrases=phrases)

@app.route('/kanji/<int:kanji_id>/phrases/add', methods=['GET', 'POST'])
def add_phrase(kanji_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para adicionar frases.', 'warning')
        return redirect(url_for('login'))

    kanji = Kanji.query.filter_by(id=kanji_id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        user_id = session['user_id']

        if not text:
            flash('O texto da frase é obrigatório.', 'danger')
            return render_template('phrase_form.html', kanji=kanji, phrase=None)

        try:
            new_phrase = Phrase(text=text, kanji_id=kanji.id, user_id=user_id)
            db.session.add(new_phrase)
            db.session.commit()
            flash('Frase adicionada com sucesso!', 'success')
            return redirect(url_for('phrase_list', kanji_id=kanji.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar Frase: {e}', 'danger')
            return render_template('phrase_form.html', kanji=kanji, phrase=None)

    return render_template('phrase_form.html', kanji=kanji, phrase=None)

@app.route('/phrase/edit/<int:phrase_id>', methods=['GET', 'POST'])
def edit_phrase(phrase_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para editar frases.', 'warning')
        return redirect(url_for('login'))

    phrase = Phrase.query.filter_by(id=phrase_id, user_id=session['user_id']).first_or_404()
    kanji = Kanji.query.filter_by(id=phrase.kanji_id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        phrase.text = request.form.get('text', '').strip()

        if not phrase.text:
            flash('O texto da frase é obrigatório.', 'danger')
            return render_template('phrase_form.html', kanji=kanji, phrase=phrase)

        try:
            db.session.commit()
            flash('Frase atualizada com sucesso!', 'success')
            return redirect(url_for('phrase_list', kanji_id=kanji.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar Frase: {e}', 'danger')
            return render_template('phrase_form.html', kanji=kanji, phrase=phrase)
    return render_template('phrase_form.html', kanji=kanji, phrase=phrase)

@app.route('/phrase/delete/<int:phrase_id>', methods=['POST'])
def delete_phrase(phrase_id):
    if 'user_id' not in session:
        flash('Você precisa estar logado para deletar frases.', 'warning')
        return redirect(url_for('login'))

    phrase = Phrase.query.filter_by(id=phrase_id, user_id=session['user_id']).first_or_404()
    kanji_id = phrase.kanji_id
    try:
        db.session.delete(phrase)
        db.session.commit()
        flash('Frase deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar Frase: {e}', 'danger')
    return redirect(url_for('phrase_list', kanji_id=kanji_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)