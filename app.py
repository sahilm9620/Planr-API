import os
from flask import Flask
from database import db
import config
from dotenv import load_dotenv
from authentication import authentication_bp
from views.algorithms import algorithms_bp
from views.general import general_bp
load_dotenv()

# creating app
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# registering blueprints
app.register_blueprint(authentication_bp)
app.register_blueprint(algorithms_bp)
app.register_blueprint(general_bp)



# Home route
@app.route('/')
def hello():
    return "hello"

# Main
if __name__ == '__main__':
    app.run()