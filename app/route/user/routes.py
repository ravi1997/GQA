from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN_or_ADMIN, verify_token, verify_user
from app.models import Account, Cadre, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import UserSchema
from . import user_bp


@user_bp.route("/")
def index():
    return "This is The waiting list user route"


@user_bp.route("/getAll", methods=["GET"])
@verify_token
@get_role
def getAll_user(role, session):

    schema = UserSchema()
    schemas = UserSchema(many=True)

    if role == "USER":
        account = Account.query.filter_by(id=session.account_id).first_or_404()
        user = User.query.filter_by(id=account.user_id).first_or_404()
        return schema.jsonify(user), 200

    users = User.query.all()
    return schemas.jsonify(users), 200


@user_bp.route("/getAllNotVerfied", methods=["GET"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def getAllNotVerified_user(session):
    schemas = UserSchema(many=True)
    users = User.query.filter_by(status=0).all()
    return schemas.jsonify(users), 200

@user_bp.route("/getUserVerify", methods=["GET"])
@verify_user
def getUserVerify_user(account):
    schemas = UserSchema(many=True)

    users = User.query.filter_by(parent_id=account.user_id,parent_status=0).all()
    return schemas.jsonify(users), 200

@user_bp.route("/getAllVerified", methods=["GET"])
@verify_user
def getAllVerified_user(account):
    schemas = UserSchema(many=True)

    users = User.query.filter_by(parent_id=account.user_id,parent_status=1).all()
    return schemas.jsonify(users), 200


@user_bp.route("/setParent/<id>", methods=["POST"])
@verify_user
def setParent_user(account,id):
    user = User.query.filter_by(id=account.user_id).first_or_404()
    user.parent_id = id
    user.parent_status = 0
    user.set_updated(account.id)
    db.session.commit()
    return jsonify({"message":"parent has been updated"}),200

@user_bp.route("/verifyChild/<id>", methods=["POST"])
@verify_user
def verifyChild_user(account,id):
    user = User.query.filter_by(id=id,parent_id=account.user_id).first_or_404()
    user.parent_status = 1
    user.set_updated(account.id)
    db.session.commit()
    return jsonify({"message":"child is verified"}),200

@user_bp.route('/getDoctors',methods = ["GET"])
@verify_user
def getDoctors_user(account):
    user = User.query.filter_by(id=account.user_id).first_or_404()
    cadre = Cadre.query.filter_by(name = "DOCTOR").first_or_404()

    users = User.query.filter_by(department_id=user.department_id,unit_id=user.unit_id,cadre_id = cadre.id).all()
    schemas = UserSchema(many=True)
    return schemas.jsonify(users), 200
