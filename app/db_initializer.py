

from app.models import Account, AccountRoles, Building, BuildingFloors, Cadre, Centre, Department, DepartmentCentres, DepartmentUnits,  Designation,  Diagnosis, Floor, FloorRooms, Plan, Role, Room, Unit, User
from app.extension import db,bcrypt
import click
from flask_app import app

@click.command('empty-db')
def empty_db_command():
	"""Drop and recreate the database."""
	drop_database()
	click.echo('Deleted and Recreated the empty database. '
			   'Run --- '
			   'flask db init, '
			   'flask db migrate, '
			   'flask db upgrade')


@click.command('seed-db')
def seed_db_command():
	"""Seed the database with initial data."""
	create_RPC()
	create_daignosis()
	create_plan()
	create_faculty_cadre()
	create_user()
	create_account()	
	click.echo('Seeded the database.')


def drop_database():
	"""Drop and recreate database schema."""
	db.reflect()
	db.drop_all()
	db.create_all()
	click.echo('Database dropped and recreated.')

def create_RPC():
	try:
		centre_rpc = Centre.query.filter_by(abbr="RPC").first()
		if not centre_rpc:
			centre_rpc = Centre(
				name="DR RP CENTER FOR OTHALMIC SCIENCE",
				abbr="RPC"
			)
			db.session.add(centre_rpc)
			db.session.commit()
			app.logger.info("Centre RPC was Added.")
		
			building_id = create_building()

			dept_id = create_department()
			
			deptCentre = DepartmentCentres(
				centre_id = centre_rpc.id,
				department_id = dept_id
			)

			db.session.add(deptCentre)
			db.session.commit()

		else:
			app.logger.info("Centre RPC already exists.")

	except Exception as e:
		app.logger.error(f"Error : {str(e)}")
		db.session.rollback()
		raise

def create_building():
	"""Create building and units."""
	try:
		building_rpc = Building.query.filter_by(abbr="RPC").first()
		if not building_rpc:
			building_rpc = Building(
				name="DR RP CENTER FOR OPTHALMIC SCIENCE",
				abbr="RPC"
			)
			db.session.add(building_rpc)
			db.session.commit()
			app.logger.info("Building RPC was Added.")
			
			Floors = [
				Floor(name="GROUND", number=0),
				Floor(number=1),
				Floor(number=2),
				Floor(number=3),
				Floor(number=4),
				Floor(number=5),
				Floor(number=6),
				Floor(number=7)
			]

			for floor in Floors:
				db.session.add(floor)
				db.session.commit()
				building_floor = BuildingFloors(
					building_id= building_rpc.id,
					floor_id=floor.id
				)
					
				db.session.add(building_floor)
				db.session.commit()
				for i in range(1, 100):
					room = Room(
						number = floor.number * 100 + i
					)
					db.session.add(room)
					db.session.commit()
					floor_room = FloorRooms(
						floor_id= floor.id,
						room_id=room.id
					)
					db.session.add(floor_room)
					db.session.commit()
			return building_rpc.id
		else:
			app.logger.info("Building RPC already exists.")
			return building_rpc.id
	except Exception as e:
		app.logger.error(f"Error creating Building: {str(e)}")
		db.session.rollback()
		raise
	

def create_department():
	"""Create department and units."""
	try:
		department_rpc = Department.query.filter_by(abbr="RPC").first()
		if not department_rpc:
			department_rpc = Department(
				name="DR RP CENTER FOR OTHALMIC SCIENCE",
				abbr="RPC"
			)
			db.session.add(department_rpc)
			db.session.commit()
			app.logger.info("Department RPC was Added.")
			
			units = [
				Unit(name="UNIT 1", abbr="U-1"),
				Unit(name="Unit 2", abbr="U-2"),
				Unit(name="Unit 3", abbr="U-3"),
				Unit(name="Unit 4", abbr="U-4"),
				Unit(name="Unit 5", abbr="U-5"),
				Unit(name="Unit 6", abbr="U-6"),
				Unit(name="OCULAR ANESTHESIA", abbr="OCU ANES")
			]

			for unit in units:
				db.session.add(unit)
				db.session.commit()
				dept_unit = DepartmentUnits(
					departmet_id= department_rpc.id,
					unit_id=unit.id
				)
				db.session.add(dept_unit)
				db.session.commit()
			return department_rpc.id
		else:
			app.logger.info("Department RPC already exists.")
			return department_rpc.id
	except Exception as e:
		app.logger.error(f"Error creating department: {str(e)}")
		db.session.rollback()
		raise

def create_daignosis():
	try:
		diagnosis_cataract = Diagnosis.query.filter_by(value="Cataract").first()
		if not diagnosis_cataract:
			diagnosis_cataract = Diagnosis(
				value="CATARACT"
			)
			db.session.add(diagnosis_cataract)
			db.session.commit()
			app.logger.info("Diagnosis Added.")
		else:
			app.logger.info("Diagnosis already exist.")

	except Exception as e:
		app.logger.error(f"Error creating Diagnosis : {str(e)}")
		db.session.rollback()
		raise

def create_plan():
	try:
		plan_surgery = Plan.query.filter_by(value="SURGERY").first()
		if not plan_surgery:
			plan_surgery = Plan(
				value="SURGERY"
			)
			db.session.add(plan_surgery)
			db.session.commit()
			app.logger.info("Plan Added.")
		else:
			app.logger.info("Plan already exist.")

	except Exception as e:
		app.logger.error(f"Error creating Plan : {str(e)}")
		db.session.rollback()
		raise


def create_faculty_cadre():
	"""Create faculty cadre and designations."""
	try:
		cadre_programmer = Cadre.query.filter_by(name="PROGRAMMER").first()
		if not cadre_programmer:
			cadre_programmer = Cadre(
				name="PROGRAMMER"
			)
			db.session.add(cadre_programmer)
			db.session.commit()
			app.logger.info("Programmer Cadre and Designations Added.")

			designations = [
				Designation(name="PROGRAMMER", abbr="PROG",cadre_id=cadre_programmer.id),
				Designation(name="SENIOR PROGRAMMER", abbr="SR PROG",cadre_id=cadre_programmer.id),
				Designation(name="ANALYST", abbr="ANALYST",cadre_id=cadre_programmer.id),
				Designation(name="SENIOR ANALYST", abbr="SR ANALYST",cadre_id=cadre_programmer.id)
			]
			for designation in designations:
				db.session.add(designation)
				db.session.commit()
		else:
			app.logger.info("Programmer Cadre and Designations already exist.")


	except Exception as e:
		app.logger.error(f"Error creating faculty cadre: {str(e)}")
		db.session.rollback()
		raise


def create_user():
	"""Create a sample user."""
	try:
		cadre_programmer = Cadre.query.filter_by(name="PROGRAMMER").first()
		designation_programmer = Designation.query.filter_by(name="PROGRAMMER", cadre_id=cadre_programmer.id).first()
		department_rpc = Department.query.filter_by(name="DR RP CENTER FOR OTHALMIC SCIENCE").first()

		existing_user = User.query.filter_by(firstname="RAVINDER", employee_id="E100000").first()
		if not existing_user:
			new_user = User(
				firstname='RAVINDER',
				middlename='',
				lastname='SINGH',
				employee_id="E100000",
				email="ravi199777@gmail.com",
				mobile="9899378106",
				department_id=department_rpc.id,
				cadre_id=cadre_programmer.id,
				designation_id=designation_programmer.id,
				officeAddress_id=1,
				unit_id=1,
				status=1
			)
			db.session.add(new_user)
			db.session.commit()
			

			app.logger.info("User Ravinder Singh Added.")
		else:
			app.logger.info("User Ravinder Singh already exists.")


	except Exception as e:
		app.logger.error(f"Error creating user: {str(e)}")
		db.session.rollback()
		raise


def create_account():
	"""Create accounts with roles."""
	try:
		user_ravinder = User.query.filter_by(firstname="RAVINDER").first()

		existing_account = Account.query.filter_by(username="ravi199777@gmail.com", user_id=user_ravinder.id).first()
		if not existing_account:
			new_account_superadmin = Account(
				username="ravi199777@gmail.com",
				password=bcrypt.generate_password_hash("Singh@1997").decode('utf-8'),
				user_id=user_ravinder.id,
				status=1
			)
			new_account_admin = Account(
				username="ravi199777@outlook.com",
				password=bcrypt.generate_password_hash("Singh@1997").decode('utf-8'),
				user_id=user_ravinder.id,
				status=1
			)

			admin = Role(name="ADMIN")
			superadmin = Role(name="SUPERADMIN")

			db.session.add(admin)
			db.session.add(superadmin)
			db.session.add(new_account_superadmin)
			db.session.add(new_account_admin)
			db.session.commit()

			account_role_admin = AccountRoles(
				account_id=new_account_admin.id,
				role_id=admin.id
			)
			account_role_superadmin = AccountRoles(
				account_id=new_account_superadmin.id,
				role_id=superadmin.id
			)

			db.session.add(account_role_admin)
			db.session.add(account_role_superadmin)
			db.session.commit()
			app.logger.info("Account Ravinder Singh Added.")
		else:
			app.logger.info("Account Ravinder Singh already exists.")


	except Exception as e:
		app.logger.error(f"Error creating account: {str(e)}")
		db.session.rollback()
		raise