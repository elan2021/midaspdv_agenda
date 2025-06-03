import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth_loja', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        nome_da_loja = request.form['register-company-name']
        nome_do_proprietario = request.form['register-owner-name']
        username = request.form['register-username']
        password = request.form['register-password']
        # domain = request.form['domain'] # Not used in schema yet
        db = get_db()
        error = None

        if not username:
            error = 'Nome de usuário é obrigatório.'
        elif not password:
            error = 'Senha é obrigatória.'
        elif not nome_da_loja:
            error = 'Nome da loja é obrigatório.'
        elif not nome_do_proprietario:
            error = 'Nome do proprietário é obrigatório.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO loja (nome_da_loja, nome_do_proprietario, nome_de_usuario, senha) VALUES (?, ?, ?, ?)",
                    (nome_da_loja, nome_do_proprietario, username, generate_password_hash(password)),
                )
                db.commit()
            except get_db().IntegrityError: # Use the specific IntegrityError from the sqlite3 connection
                error = f"Usuário {username} já está registrado."
            else:
                flash('Registro bem-sucedido! Faça o login.')
                return redirect(url_for("auth_loja.login")) # Or redirect to main page which shows login

        flash(error)

    return render_template('login_register.html') # Or whatever the main page is

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['login-username'] # Assuming login form fields are 'login-username' and 'login-password'
        password = request.form['login-password'] # Assuming login form fields are 'login-username' and 'login-password'
        db = get_db()
        error = None
        loja = db.execute(
            'SELECT * FROM loja WHERE nome_de_usuario = ?', (username,)
        ).fetchone()

        if loja is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(loja['senha'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['loja_id'] = loja['id']
            session['username'] = loja['nome_de_usuario']
            # Redirect to a dashboard or main app page after login
            # For now, let's redirect to the main page, it might show a different state
            flash(f"Login bem-sucedido, {session['username']}!")
            return redirect(url_for('main_index')) # Assumes a main_index route exists

        flash(error)

    return render_template('login_register.html') # Or whatever the main page is

@bp.before_app_request
def load_logged_in_loja():
    loja_id = session.get('loja_id')

    if loja_id is None:
        g.loja = None
    else:
        g.loja = get_db().execute(
            'SELECT * FROM loja WHERE id = ?', (loja_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logout bem-sucedido.')
    return redirect(url_for('main_index')) # Assumes a main_index route exists

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.loja is None:
            return redirect(url_for('auth_loja.login'))
        return view(**kwargs)
    return wrapped_view
