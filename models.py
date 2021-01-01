from database import db
from sqlalchemy.dialects.postgresql import JSON


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

    ratings = db.relationship("UserRatings", backref='user')
    otpstore = db.relationship("OTPS", backref='user')
    wishlistplace = db.relationship("WishlistPlace", backref='user')
    wishlistcity = db.relationship("WishlistCity", backref='user')

class Cities(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.String(500))
    image = db.Column(db.String(200))

    pois = db.relationship("Pois", backref='city')
    ratings = db.relationship("UserRatings", backref='city')
    wishlistcity = db.relationship("WishlistCity", backref='city')

class UserRatings(db.Model):
    __tablename__ = 'user_ratings'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))



class Pois(db.Model):
    __tablename__ = 'pois'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    opening_time = db.Column(db.Float)
    closing_time = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    time_to_spend = db.Column(db.Float)
    category = db.Column(db.String(15))
    average_rating = db.Column(db.Float)
    image = db.Column(db.String(200))
    description = db.Column(db.String(500))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

    ratings = db.relationship("UserRatings", backref='poi')
    wishlistplace = db.relationship("WishlistPlace", backref='poi')

class OTPS(db.Model):
    __tablename__= 'otps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(50))
    otp = db.Column(db.String(6))

class WishlistPlace(db.Model):
    __tablename__= 'wishlistplace'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'))
    value = db.Column(db.Boolean)

class WishlistCity(db.Model):
    __tablename__= 'wishlistcity'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    value = db.Column(db.Boolean)