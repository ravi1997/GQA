from sqlalchemy import DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.extension import db, bcrypt
from datetime import datetime
from sqlalchemy import func

# MODELS
class UserState(SQLAlchemyEnum):
    CREATED  = "created"
    ACTIVE   = "active"
    BLOCKED  = "blocked"
    DISABLED = "disabled"
    DELETED  = "deleted"

class UserRole(SQLAlchemyEnum):
    SUPERADMIN = "superadmin"
    TRAINER = "trainer"
    USER = "user"
    GUEST = "guest"

class ValidState(SQLAlchemyEnum):
    VALID = "valid"
    INVALID = "invalid"

# MAIN MODELS
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    pathname = db.Column(db.String(500), nullable=False)
    lineno = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

class Client(db.Model):
    __tablename__ = "clients"  # Updated table name to be plural
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(DateTime, server_default=func.now())  # Corrected attribute name
    client_session_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), index=True, nullable=True,server_default = '1')  # Corrected table name
    status = db.Column(SQLAlchemyEnum(ValidState), index=True, nullable=False, server_default=ValidState.VALID)
    ip = db.Column(db.String(16), nullable=True)
    salt = db.Column(db.String(256),nullable=False)

    otp_id = db.Column(db.Integer, ForeignKey('otps.id'), index=True, nullable=True)  # Corrected table name
    user = relationship("User", back_populates="clients")
    otp = relationship("OTP", back_populates="client")
    
    def __init__(self, client_session_id, user_id=None, ip=None):
        self.client_session_id = client_session_id
        self.user_id = user_id
        self.ip = ip

    def isValid(self):
        return self.status == ValidState.VALID

    def setStatus(self, status):
        self.status = status

    def __repr__(self):
        return (f"<Client(id={self.id}, client_session_id='{self.client_session_id}', "
                f"user_id={self.user_id}, status='{self.status}', ip='{self.ip}')>")

class OTP(db.Model):
    __tablename__ = "otps"  # Updated table name to be plural
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('clients.id'), index=True, unique=True, nullable=False)  # Corrected table name
    otp = db.Column(db.String(7), nullable=False)
    created_at = db.Column(DateTime, server_default=func.now(), nullable=False)
    status = db.Column(SQLAlchemyEnum(ValidState), index=True, nullable=False, server_default=ValidState.VALID)
    wrongAttempt = db.Column(db.Integer, server_default="0")
    sendAttempt = db.Column(db.Integer, server_default="0")

    client = relationship("Client", back_populates="otp")
    
    def __init__(self, client_id, otp):
        self.client_id = client_id
        self.otp = otp

    def __repr__(self):
        return (f"<OTP(id={self.id}, client_id={self.client_id}, otp='{self.otp}', "
                f"status='{self.status}', created_at='{self.created_at}')>")

class Organisation(db.Model):
    __tablename__ = "organisations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index=True, nullable=False)
    state = db.Column(db.String(30), index=True, nullable=False)
    district = db.Column(db.String(30), index=True, nullable=False)
    address = db.Column(db.String(30), index=True, nullable=False)

    users = relationship("User", back_populates="organisation")

    def __repr__(self):
        return (f"<Organisation(id={self.id}, name='{self.name}', state='{self.state}', "
                f"district='{self.district}', address='{self.address}')>")

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), index=True, nullable=False)
    middlename = db.Column(db.String(30), index=True, nullable=True)
    lastname = db.Column(db.String(30), index=True, nullable=True)
    dob = db.Column(DateTime, index=True, nullable=False)
    mobile = db.Column(db.String(30), nullable=False)

    organization_id = db.Column(db.Integer, ForeignKey('organisations.id'), index=True, nullable=False)  # Corrected table name

    role = db.Column(SQLAlchemyEnum(UserRole), index=True, nullable=False, server_default=UserRole.GUEST)
    status = db.Column(SQLAlchemyEnum(UserState), index=True, nullable=False, server_default=UserState.CREATED)

    created_by = db.Column(db.String(30), index=True, nullable=False, server_default="1")
    created_at = db.Column(DateTime, server_default=func.now(), nullable=False)
    updated_by = db.Column(db.String(30), index=True, nullable=False, server_default="1")
    updated_at = db.Column(DateTime, server_default=func.now(), nullable=False)

    clients = relationship("Client", back_populates="user")
    organisation = relationship("Organisation", back_populates="users")

    def __init__(self, firstname, mobile, dob, organization_id, created_by, middlename=None, lastname=None,
                 status=UserState.CREATED, updated_by=None, updated_at=None):
        self.firstname = firstname.upper()
        self.middlename = (middlename.upper() if middlename else None)
        self.lastname = (lastname.upper() if lastname else None)

        self.dob = dob
        self.mobile = mobile
        self.organization_id = organization_id
        self.status = status
        self.created_by = created_by
        self.updated_by = updated_by or created_by  # Defaults to created_by if not provided

        if updated_at is not None:
            self.updated_at = updated_at

    def __repr__(self):
        return (f"<User(id={self.id}, name='{self.firstname} {self.middlename or ''} {self.lastname or ''}', "
                f"mobile='{self.mobile}', organization_id={self.organization_id}, "
                f"status='{self.status}', role='{self.role}')>")


    def isDeleted(self):
        return self.status == UserState.DELETED
    
    def isActive(self):
        return self.status == UserState.ACTIVE
    
    def isBlocked(self):
        return self.status == UserState.BLOCKED
    