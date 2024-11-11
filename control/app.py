from flask import Flask, flash
from urllib.parse import quote
from control.auth import auth_bp, admin_bp, users_bp
from control.views import views
from control.extensions import migrate, login_manager, db
from control.models import User
from flask_login import login_user, logout_user, login_required, current_user, LoginManager

def create_app():
    app = Flask(__name__)
    app.secret_key = 'heisenberg'

    app.register_blueprint(views)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(users_bp,  url_prefix='/users')

    
    # Initialize extensions
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Loginto12@localhost/control'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

   
    
    def urlencode_filter(s):
        return quote(s)

    app.jinja_env.filters['urlencode'] = urlencode_filter


    def urlencode_filter(s):
        return quote(s)

    app.jinja_env.filters['urlencode'] = urlencode_filter

    with app.app_context():
     db.create_all()

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  # Adjust according to your user model

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None
    
   
