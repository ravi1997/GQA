from flask import jsonify,current_app
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token
from app.models import Account
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import AccountSchema, UserSchema
from . import account_bp


@account_bp.route("/")
def index():
    return "This is The waiting list account route"


@account_bp.route("/getAll", methods=["GET"])
@verify_token
@get_role
def getAll_account(role, session):

    schema = AccountSchema()
    schemas = AccountSchema(many=True)

    if role == "USER":
        account = Account.query.filter_by(id=session.account_id).first_or_404()
        return schema.jsonify(account), 200

    accounts = Account.query.all()
    return schemas.jsonify(accounts), 200


@account_bp.route("/getAllNotVerfied", methods=["GET"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def getAllNotVerified_account(session):
    schemas = AccountSchema(many=True)
    accounts = Account.query.filter_by(status=0).all()
    return schemas.jsonify(accounts), 200


@account_bp.route("/changePassword",methods=["PUT"])
@verify_token
@verify_body
def change_password_account(body,session):
    account=Account.query.filter_by(id=session.account_id).first()
    password =body["password"]

    if password is None:
        return jsonify({"message":"username is required"}),400
    
    account.password = bcrypt.generate_password_hash(password).decode(
                "utf-8"
            )
    
    db.session.commit()

