from flask import Blueprint, request, jsonify, current_app as app
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from emailer import send
import random
import math

authentication_bp = Blueprint('authentication_bp', __name__)

from models import Users
from models import OTPS
from database import db

# ============================
#   OTP GENERATOR
# ============================

def OTP_generator():
    digits = [i for i in range(0, 10)]
    random_str = ""

    for i in range(6):
        index = math.floor(random.random()*10)
        random_str += str(digits[index])

    return random_str


# ============================
#   CHECK PRESENCE OF TOKEN
# ============================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authentication')

        if not token:
            return jsonify({
                'message': 'Token missing'
            }), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({
                'message': 'Token invalid',
            }), 401

        return f(current_user, *args, **kwargs)
    return decorated


# ====================
#     USER SIGNUP
# ====================

@authentication_bp.route('/signup', methods=['POST'])
def user_signup():
    data = request.get_json()

    user = Users.query.filter_by(email=data['email']).first()

    if user:
        return jsonify(
            {
                'success': False,
                'message': 'User already exists!'
            }
        ), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(
        public_id=str(uuid.uuid4()),
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        admin=False
    )

    token = jwt.encode(
            {
                'public_id': new_user.public_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            app.config['SECRET_KEY']
        )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {
            'success': True,
            'message': 'Signup successfull',
            'token': token,
            'name': new_user.name,
            'email': new_user.email
        }
    )


# ====================
#     USER LOGIN
# ====================

@authentication_bp.route('/login', methods=['POST'])
def user_login():
    data = request.get_json()

    user = Users.query.filter_by(email=data['email']).first()

    # user not found
    if not user:
        return jsonify(
            {
                'success': False,
                'message': 'Authentication failed'
            }
        ), 401

    # password matched
    if check_password_hash(user.password, data['password']):
        token = jwt.encode(
            {
                'public_id': user.public_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            app.config['SECRET_KEY']
        )
        return jsonify(
            {
                'success': True,
                'message': 'Login successfull',
                'token': token,
                'name': user.name,
                'email': user.email
            }
        )

    # password not matched
    return jsonify(
        {
            'success': False,
            'message': 'Authentication failed'
        }
    ), 401

# ====================
#     GET ALL USERS
# ====================

@authentication_bp.route('/users', methods = ['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({
            'message': 'Cannot perform that function!'
        })

    users = Users.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})

# ====================
#   PASSWORD CHANGE
# ====================
@authentication_bp.route('/change-password', methods=['POST'])
@token_required
def changepassword(current_user):

    public_id = current_user.public_id

    user = Users.query.filter_by(public_id = public_id).first()

    # user not found
    # if not user:
    #     return jsonify(
    #         {
    #             'success': False,
    #             'message': 'Authentication failed'
    #         }
    #     ), 401

    data = request.get_json()

    # password matching
    if check_password_hash(user.password, data['password']):
        if data['newpassword'] == data['confirmpassword']:
            hashed_password = generate_password_hash(data['newpassword'], method='sha256')
            user.password = hashed_password
            db.session.commit()
            return jsonify(
                {
                    'success': True,
                    'message': 'Password changed successfully!',
                }
            )
        else:
            return jsonify(
                {
                    'success': False,
                    'message': 'Passwords did not match. Enter again!',
                }
            )

    # password not matched
    return jsonify(
        {
            'success': True,
            'message': 'Please enter correct password!'
        }
    ), 200

# ====================
#   FORGOT PASSWORD
# ====================
@authentication_bp.route('/forgot-password', methods=['POST'])
def forgotpassword():
    data = request.get_json()

    user = Users.query.filter_by(email = data['email']).first()

    # user not found
    if not user:
        return jsonify(
            {
                'success': False,
                'message': 'User not found!'
            }
        ), 401

    # token = jwt.encode(
    #         {
    #             'public_id': user.public_id,
    #             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    #         },
    #         app.config['SECRET_KEY']
    #     )

    OTP = OTP_generator()

    row = OTPS.query.filter_by(user_id = user.id).first()

    if not row:
        new_otp = OTPS(
        user_id = user.id,
        email = data['email'],
        otp = OTP
        )

        db.session.add(new_otp)
        db.session.commit()

    else:
        row.otp = OTP
        db.session.commit()

    # Call to send email function in emailer.py
    status = send(data['email'], OTP)

    # token_str = token.decode("utf-8")
    lnk = 'http://127.0.0.1:5000/reset-password?token='

    if status == 202:

        return jsonify(
            {
                'success': True,
                'message': 'Email sent succesfully!!',
                'OTP': OTP,
                'Link': lnk
            }
        ), 200

    else:

        return jsonify(
            {
                'success': False,
                'message': 'Please Try Again!!',
            }
        ), 200


# ====================
#   VERIFY OTP
# ====================
@authentication_bp.route('/verify-otp', methods=['POST'])
def verifyotp():
    data = request.get_json()

    row = OTPS.query.filter_by(email=data['email'],otp=data['otp']).first()

    if not row:
        return jsonify(
            {
                'success': False,
                'message': 'OTP is Incorrect. Enter Again!'
            }
        ), 200

    if data['otp'] == row.otp:
        return jsonify(
            {
                'success': True,
                'message': 'Verification Successful!'
            }
        ), 200


# ====================
#   RESET PASSWORD
# ====================
@authentication_bp.route('/reset-password', methods=['POST'])
def resetpassword():

    passw = request.get_json()

    user = Users.query.filter_by(email = passw['email']).first()

    if passw['newpassword'] == passw['confirmpassword']:
        hashed_password = generate_password_hash(passw['newpassword'], method='sha256')
        user.password = hashed_password
        db.session.commit()
        return jsonify(
            {
                'success': True,
                'message': 'Password changed successfully!',
            }
        ), 200
    else:
        return jsonify(
            {
                'success': False,
                'message': 'Password did not match. Enter again!',
            }
        )
