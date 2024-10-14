from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_body
from app.models import Account, Building, BuildingFloors, Cadre, Department, DepartmentUnits, Designation, Floor, FloorRooms, Room, Unit,  User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import AccountSchema, BuildingSchema, CadreSchema, DepartmentSchema, DesignationSchema, FloorSchema, RoomSchema, UnitSchema, UserSchema
from app.util import generate_strong_password, send_sms
from . import public_bp


@public_bp.route("/")
def index():
    return "This is The waiting list public route"

@public_bp.route("/getBuildings", methods=["GET"])
def get_all_active_Buildings():
    try:
        schema = BuildingSchema(many=True)
        diagnosises = Building.query.filter_by(deleted=0).all()
        return schema.jsonify(diagnosises), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@public_bp.route("/getFloors/<building_id>", methods=["GET"])
def getfloorBybuilding(building_id):
    schema = FloorSchema(many=True)
    building = Building.query.filter_by(id=building_id).first_or_404()

    if building.isDeleted():
        return jsonify({"message":"Building is deleted"}),400

    floor_ids = BuildingFloors.query.filter_by(building_id=building_id)
    floors = []
    for building_floor_id in floor_ids:
        floor = Floor.query.filter_by(id=building_floor_id.floor_id).first()
        if floor.isDeleted() == False:
            floors.append(floor)

    return schema.jsonify(floors), 200


@public_bp.route("/getRooms/<floor_id>", methods=["GET"])
def getRoomByfloor(floor_id):
    """
    Route to get rooms for a specific floor by ID.
    """
    schema = RoomSchema(many=True)
    floor = Floor.query.filter_by(id=floor_id).first_or_404()

    if floor.isDeleted():
        return jsonify({"message":"Floor is deleted"}),400

    floor_ids = FloorRooms.query.filter_by(floor_id=floor_id)
    rooms = []
    for floor_room_id in floor_ids:
        room = Room.query.filter_by(id=floor_room_id.room_id).first()
        if room.isDeleted() == False:
            rooms.append(room)
    return schema.jsonify(rooms), 200


@public_bp.route("/getDepartments", methods=["GET"])
def get_all_active_departments():
    """
    Route to get all active departments.
    """
    try:
        schema = DepartmentSchema(many=True)
        departments = Department.query.filter_by(deleted=0).all()
        return schema.jsonify(departments), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@public_bp.route("/getUnits/<department_id>", methods=["GET"])
def getunitByDepartment(department_id):
    """
    Route to get units for a specific department by ID.
    """
    schema = UnitSchema(many=True)
    department = Department.query.filter_by(id=department_id).first_or_404()

    if department.isDeleted():
        return jsonify({"message":"Department is deleted"}),400

    department_ids = DepartmentUnits.query.filter_by(department_id=department_id)
    units = []
    for department_unit_id in department_ids:
        unit = Unit.query.filter_by(id=department_unit_id.unit_id).first()
        if unit.isDeleted() == False:
            units.append(unit)

    return schema.jsonify(units), 200


@public_bp.route("/getCadres", methods=["GET"])
def get_all_active_cadres():
    """
    Route to get all active cadres.
    """
    try:
        schema = CadreSchema(many=True)
        cadres = Cadre.query.filter_by(deleted=0).all()
        return schema.jsonify(cadres), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@public_bp.route("/getDesignations/<cadre_id>", methods=["GET"])
def getdesignation_cadre(cadre_id):

    schema = DesignationSchema(many=True)
    cadre = Cadre.query.filter_by(id=cadre_id).first_or_404()

    if cadre.isDeleted():
        return jsonify({"message":"Cadre is deleted"}),400

    cadre_ids = Designation.query.filter_by(cadre_id=cadre_id,deleted=0).all()
    designations = []
    for designation in cadre_ids:
        designations.append(designation)

    return schema.jsonify(designations), 200


@public_bp.route("/createUser", methods=["POST"])
@verify_body
def create_user(request_data):
    schema = UserSchema()

    try:
        errors = schema.validate(request_data)
        if errors:
            return jsonify(errors), 400

        user_data = schema.load(request_data)
        employee_id = user_data.employee_id

        user = User.query.filter_by(employee_id=employee_id).first()
        if user is None:
            db.session.add(user_data)
            db.session.commit()
            current_app.logger.info(f"User is created : {employee_id}")
            return (
                jsonify(
                    {
                        "message": f"User is created : {employee_id}",
                        "user": schema.dump(user_data),
                    }
                ),
                200,
            )
        else:
            current_app.logger.info(f"User already : {employee_id}")
            user.firstname = user_data.firstname.upper()
            if user_data.middlename is not None:
                user.middlename = user_data.middlename.upper()
            if user_data.lastname is not None:
                user.lastname = user_data.lastname.upper()

            user.email = user_data.email
            user.mobile = user_data.mobile
            user.email2 = user_data.email2
            user.email3 = user_data.email3
            user.mobile2 = user_data.mobile2
            user.mobile3 = user_data.mobile3
            user.officeAddress_id = user_data.officeAddress_id
            user.department_id = user_data.department_id
            user.unit_id = user_data.unit_id
            user.designation_id = user_data.designation_id
            user.cadre_id = user_data.cadre_id
            user.status = user_data.status
            user.verified_by = user_data.verified_by
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": f"User already : {employee_id}",
                        "user": schema.dump(user),
                    }
                ),
                200,
            )
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400


@public_bp.route("/createAccount", methods=["POST"])
@verify_body
def create_account(request_data):
    schema = AccountSchema()

    try:
        errors = schema.validate(request_data)
        if errors:
            return jsonify(errors), 400

        account_data = schema.load(request_data)
        account_id = account_data.username

        account = Account.query.filter_by(username=account_id).first()
        if account is None:
            password = account_data.password
            account_data.password = bcrypt.generate_password_hash(password).decode(
                "utf-8"
            )
            db.session.add(account_data)
            db.session.commit()
            current_app.logger.info(f"Account is created : {account_id}")
            return (
                jsonify(
                    {
                        "message": f"Account is created : {account_id}",
                        "account": schema.dump(account_data),
                    }
                ),
                200,
            )
        else:
            current_app.logger.info(f"Account already : {account_id}")
            return jsonify({"message": f"Account already : {account_id}"}), 400

    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400


@public_bp.route("/forgetPassword", methods=["POST"])
@verify_body
def forget_password_account(request_data):
    username = request_data["username"]
    emp_id = request_data["emp_id"]

    if username is None:
        return jsonify({"message":"username is required"}),400
    if emp_id is None:
        return jsonify({"message":"emp_id is required"}),400
    account = Account.query.filter_by(username=username).first()
    if account is None:
        return jsonify({"message":"Account not found"}),400
    user = User.query.filter_by(id=account.user_id).first()
    if account is None:
        return jsonify({"message":"User not found"}),400

    if user.employee_id == emp_id:
        password = generate_strong_password()
        account.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # Todo : send new password to mobile
        user = User.query.filter_by(id=account.user_id).first()
        status_code = send_sms(user.mobile,password)
        if status_code!=200 or status_code != 201:
            return jsonify({"message":"Something went wrong. Please try again after some time"}),400
        account.status = 2
        db.session.commit()
        return jsonify({"message": "Account password has been updated"}), 200
    return jsonify({"message":"emp_id not belong to user"}),400