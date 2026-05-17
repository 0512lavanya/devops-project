from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, BloodRequest, Inventory, AuditLog
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# --- AUTH ---
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
        
    return jsonify({"error": "Invalid credentials"}), 401

# --- SMART MATCHING ---
@api_bp.route('/match/<int:request_id>', methods=['GET'])
@jwt_required()
def smart_match(request_id):
    blood_request = BloodRequest.query.get_or_404(request_id)
    
    # Logic: Find donors with matching blood type, who are available, in the same location
    matching_donors = User.query.filter_by(
        role='donor',
        blood_type=blood_request.blood_type_needed,
        location=blood_request.hospital, # Assuming hospital implies location for simplicity
        is_available=True
    ).all()
    
    results = [{"id": d.id, "username": d.username, "email": d.email} for d in matching_donors]
    
    # Audit log
    audit = AuditLog(user_id=get_jwt_identity(), action=f"API Smart Match for Request {request_id}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"matches": results, "count": len(results)}), 200

# --- INVENTORY ---
@api_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'hospital' and user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    inventory = Inventory.query.filter_by(hospital_id=user.id).all()
    return jsonify([{"blood_type": i.blood_type, "units": i.units_available} for i in inventory]), 200

@api_bp.route('/inventory/update', methods=['POST'])
@jwt_required()
def update_inventory():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'hospital':
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    blood_type = data.get('blood_type')
    units = data.get('units')
    
    inv = Inventory.query.filter_by(hospital_id=user.id, blood_type=blood_type).first()
    if inv:
        inv.units_available = units
    else:
        inv = Inventory(hospital_id=user.id, blood_type=blood_type, units_available=units)
        db.session.add(inv)
        
    # Audit log
    audit = AuditLog(user_id=user.id, action=f"API Inventory Update: {blood_type} to {units}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"status": "success"}), 200
