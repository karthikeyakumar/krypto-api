from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import jwt
import datetime


app = Flask(__name__)

app.config["SECRET_KEY"] = "004f2af45d3a4e161a7dd2d17fdae47f"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///krypto.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    admin = db.Column(db.Boolean)


class coins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    price = db.Column(db.Integer)
    email = db.Column(db.String(120))
    high = db.Column(db.Boolean)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]

        if not token:
            return jsonify({"message": "a valid token is missing"})
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Users.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "token is invalid"})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route("/register", methods=["POST"])
def signup_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = Users(
        public_id=str(uuid.uuid4()),
        name=data["name"],
        password=hashed_password,
        email=data["email"],
        admin=False,
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "registered successfully"})


@app.route("/login", methods=["POST"])
def login_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            "could not verify", 401, {"Authentication": 'login required"'}
        )

    user = Users.query.filter_by(name=auth.username).first()
    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
            },
            app.config["SECRET_KEY"],
            "HS256",
        )

        return jsonify({"token": token})

    return make_response(
        "could not verify", 401, {"Authentication": '"login required"'}
    )


@app.route("/users", methods=["GET"])
def get_all_users():

    users = Users.query.all()
    result = []
    for user in users:
        user_data = {}
        user_data["public_id"] = user.public_id
        user_data["name"] = user.name
        user_data["password"] = user.password
        user_data["admin"] = user.admin
        user_data["email"] = user.email
        result.append(user_data)
    return jsonify({"users": result})


@app.route("/users/<public_id>", methods=["PUT"])
@token_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    user = Users.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})
    user.admin = True
    db.session.commit()
    return jsonify({"message": "The user has been promoted!"})


@app.route("/alert/create", methods=["POST"])
@token_required
def create_alert(current_user):
    data = request.get_json()
    new_alert = coins(
        price=data["price"],
        high=data["high"],
        email=current_user.email,
        user_id=current_user.id,
    )
    db.session.add(new_alert)
    db.session.commit()
    return jsonify({"message": "new alert created"})


@app.route("/alert/delete/<alert_id>", methods=["DELETE"])
@token_required
def delete_alert(current_user, alert_id):
    alert = coins.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if not alert:
        return jsonify({"message": "alert does not exist"})

    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": "alert deleted"})


@app.route("/alert/all", methods=["GET"])
@token_required
def get_alerts(current_user):

    alert = coins.query.filter_by(user_id=current_user.id).all()
    output = []
    for i in alert:
        alert_data = {}
        alert_data["id"] = i.id
        alert_data["price"] = i.price
        alert_data["high"] = i.high
        alert_data["email"] = i.email
        output.append(alert_data)

    return jsonify({"list_of_alerts": output})


if __name__ == "__main__":
    app.run(debug=True)
