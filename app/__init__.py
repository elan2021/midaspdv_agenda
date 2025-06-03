import os
from flask import Flask, render_template, g # Added render_template and g

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # Change for production
        DATABASE=os.path.join(app.instance_path, 'lojas.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register database functions
    from . import db
    db.init_app(app)

    # Register auth_loja blueprint
    from . import auth_loja
    app.register_blueprint(auth_loja.bp)

    # Define a simple main route
    @app.route('/')
    def main_index():
        # If user is logged in, perhaps redirect to a dashboard
        # For now, always show login/register page
        return render_template('login_register.html')

    # Example of a route that requires login (can be in a different blueprint later)
    # This requires g to be imported from flask
    @app.route('/dashboard')
    @auth_loja.login_required
    def dashboard():
        return f"Welcome to your dashboard, {g.loja['nome_de_usuario']}!"

    return app
