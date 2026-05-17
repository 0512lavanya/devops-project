from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    blood_type = db.Column(db.String(5))
    location = db.Column(db.String(100))
    role = db.Column(db.String(20), default='donor') # 'donor', 'hospital', 'admin'
    is_available = db.Column(db.Boolean, default=True) # Live availability toggle
    
    donations = db.relationship('DonationHistory', backref='donor', lazy='dynamic')
    requests = db.relationship('BloodRequest', foreign_keys='BloodRequest.user_id', backref='patient_user', lazy='dynamic')
    health_records = db.relationship('HealthRecord', backref='donor', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_file_path = db.Column(db.String(255), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    is_eligible = db.Column(db.Boolean, default=True)
    uploaded_on = db.Column(db.DateTime, default=datetime.utcnow)

class DonationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hospital_name = db.Column(db.String(150), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pending Approval') # Pending Approval, Fit, Unfit, Completed
    health_notes = db.Column(db.Text, nullable=True)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    assigned_donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    diagnosis = db.Column(db.String(255), nullable=True)
    blood_type_needed = db.Column(db.String(5), nullable=False)
    units_required = db.Column(db.Integer, default=1)
    urgency = db.Column(db.String(20), nullable=False)
    is_emergency = db.Column(db.Boolean, default=False)
    doctor_reference = db.Column(db.String(100), nullable=True)
    report_file_path = db.Column(db.String(255), nullable=True)
    
    hospital = db.Column(db.String(100), nullable=False)
    accepting_hospital = db.Column(db.String(100), nullable=True) # Cross-hospital
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Assigned, Fulfilled
    requested_on = db.Column(db.DateTime, default=datetime.utcnow)

class BroadcastMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Normal') # Normal, Emergency
    sender_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hospital_name = db.Column(db.String(100))
    request_id = db.Column(db.Integer, db.ForeignKey('blood_request.id'), nullable=True)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blood_type = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
