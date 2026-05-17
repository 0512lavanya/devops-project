import os
import redis
import shutil
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, DonationHistory, BloodRequest, HealthRecord, Appointment, Inventory, AuditLog, BroadcastMessage
from app import db, limiter

main = Blueprint('main', __name__)

try:
    redis_client = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, db=0, decode_responses=True)
except Exception:
    redis_client = None

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/urgent-requests')
def urgent_requests():
    # Public view for all urgent requests
    requests = BloodRequest.query.filter(
        BloodRequest.status.in_(['Pending', 'Accepted', 'Assigned'])
    ).order_by(
        BloodRequest.is_emergency.desc(), BloodRequest.requested_on.desc()
    ).all()
    return render_template('urgent_requests.html', requests=requests)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            return render_template('login.html', error="Invalid username or password")
            
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        blood_type = request.form.get('blood_type', '')
        location = request.form.get('location')
        role = request.form.get('role', 'donor')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return render_template('signup.html', error="User already exists")

        user = User(username=username, email=email, blood_type=blood_type, location=location, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('signup.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
        
    if current_user.role == 'hospital':
        # Local requests
        local_requests = BloodRequest.query.filter_by(user_id=current_user.id).order_by(BloodRequest.requested_on.desc()).all()
        
        # Global requests (Cross-Hospital)
        global_requests = BloodRequest.query.filter(BloodRequest.user_id != current_user.id).order_by(
            BloodRequest.is_emergency.desc(), BloodRequest.requested_on.desc()
        ).all()
        
        # Calculate Smart Match Indicators
        for gr in global_requests:
            gr.matching_donors_count = User.query.filter_by(
                role='donor', blood_type=gr.blood_type_needed, is_available=True, location=current_user.location
            ).count()
        
        # Broadcast Messages
        broadcasts = BroadcastMessage.query.order_by(BroadcastMessage.timestamp.desc()).limit(10).all()
        
        # Pending & Approved Donors
        pending_donors = DonationHistory.query.filter_by(hospital_name=current_user.username, status='Pending Approval').all()
        for pd in pending_donors:
            pd.health_record = HealthRecord.query.filter_by(user_id=pd.user_id).order_by(HealthRecord.uploaded_on.desc()).first()
            
        approved_donors = DonationHistory.query.filter_by(hospital_name=current_user.username, status='Fit').all()
        for ad in approved_donors:
            ad.total_donations = DonationHistory.query.filter_by(user_id=ad.user_id, status='Completed').count()
            
        completed_donations = DonationHistory.query.filter_by(hospital_name=current_user.username, status='Completed').order_by(DonationHistory.donation_date.desc()).all()
        timeline = AuditLog.query.filter_by(user_id=current_user.id).order_by(AuditLog.timestamp.desc()).limit(15).all()
        
        stats = {
            "total_handled": len(completed_donations),
            "active_requests": BloodRequest.query.filter_by(user_id=current_user.id, status='Pending').count(),
            "emergencies": BloodRequest.query.filter_by(user_id=current_user.id, is_emergency=True, status='Pending').count(),
            "pending_verifications": len(pending_donors)
        }
        
        return render_template('dashboard.html', requests=local_requests, global_requests=global_requests, 
                               broadcasts=broadcasts, pending_donors=pending_donors, 
                               approved_donors=approved_donors, stats=stats, 
                               completed_donations=completed_donations, timeline=timeline)
        
    # Donor Dashboard
    donations = DonationHistory.query.filter_by(user_id=current_user.id).order_by(DonationHistory.donation_date.desc()).all()
    # 10. Health Record Vault & 1. Smart Eligibility
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.uploaded_on.desc()).all()
    latest_record = records[0] if records else None
    
    is_eligible = True
    wait_days = 0
    unfit_reason = None
    next_eligible_date = datetime.utcnow()
    
    if not latest_record:
        is_eligible = False
        unfit_reason = "Missing health record. Please upload a report to become eligible."
    elif (datetime.utcnow() - latest_record.uploaded_on).days > 180:
        is_eligible = False
        unfit_reason = "Health report is older than 6 months and has expired. Please upload a new one."
    
    completed_donations = [d for d in donations if d.status == 'Completed']
    if completed_donations and is_eligible:
        last_donation = completed_donations[0].donation_date
        days_since_last = (datetime.utcnow() - last_donation).days
        if days_since_last < 90:
            is_eligible = False
            wait_days = 90 - days_since_last
            next_eligible_date = last_donation + timedelta(days=90)
            
    unfit_donations = [d for d in donations if d.status == 'Unfit']
    if unfit_donations and is_eligible:
        last_unfit = unfit_donations[0]
        if (datetime.utcnow() - last_unfit.donation_date).days < 30:
            is_eligible = False
            unfit_reason = f"Marked unfit on {last_unfit.donation_date.strftime('%Y-%m-%d')}. Notes: {last_unfit.health_notes}"
            next_eligible_date = last_unfit.donation_date + timedelta(days=30)
            wait_days = (next_eligible_date - datetime.utcnow()).days

    # 2. Advanced Stats Panel
    total_applications = len(donations)
    total_donations = len(completed_donations)
    lives_saved = total_donations * 3
    hospitals_donated_to = len(set([d.hospital_name for d in completed_donations]))
    approval_rate = int((total_donations / total_applications) * 100) if total_applications > 0 else 100
    emergency_donations = min(total_donations, 2)  # Simulated for now
    rejection_reasons = list(set([d.health_notes for d in unfit_donations if d.health_notes]))
    
    stats = {
        'total_donations': total_donations,
        'lives_saved': lives_saved,
        'hospitals_donated_to': hospitals_donated_to,
        'approval_rate': approval_rate,
        'emergency_donations': emergency_donations,
        'rejection_reasons': rejection_reasons
    }

    # 13. Gamification Badges
    badges = []
    badges.append({"name": "🥉 First Donation", "unlocked": total_donations >= 1, "progress": min(1, total_donations)/1 * 100})
    badges.append({"name": "🥈 Life Saver (5)", "unlocked": total_donations >= 5, "progress": min(5, total_donations)/5 * 100})
    badges.append({"name": "🥇 Lifesaver (10+)", "unlocked": total_donations >= 10, "progress": min(10, total_donations)/10 * 100})
    if emergency_donations >= 1: badges.append({"name": "🚑 Emergency Hero", "unlocked": True, "progress": 100})

    # Hospital-wise tracking
    hospital_wise = {}
    for d in completed_donations:
        if d.hospital_name not in hospital_wise:
            hospital_wise[d.hospital_name] = {'count': 0, 'last_date': d.donation_date}
        hospital_wise[d.hospital_name]['count'] += 1

    # Urgent Needs & Broadcasts (Notify Matching Donors only if possible)
    emergency_requests = BloodRequest.query.filter_by(is_emergency=True, status='Pending').all()
    # 4. Emergency Priority Engine logic: Match blood first
    emergency_requests.sort(key=lambda r: (r.blood_type_needed != current_user.blood_type, r.requested_on))
    
    broadcasts = BroadcastMessage.query.order_by(BroadcastMessage.timestamp.desc()).limit(5).all()
    

    def is_compatible(donor_bg, patient_bg):
        if not donor_bg or not patient_bg: return False
        compat_map = {
            'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'O+': ['O+', 'A+', 'B+', 'AB+'],
            'A-': ['A-', 'A+', 'AB-', 'AB+'],
            'A+': ['A+', 'AB+'],
            'B-': ['B-', 'B+', 'AB-', 'AB+'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB-', 'AB+'],
            'AB+': ['AB+']
        }
        return patient_bg in compat_map.get(donor_bg, [])

    hospitals = User.query.filter_by(role='hospital').all()
    
    # 3. Hospital Intelligence Layer & 5. AI Match Recommender
    hospital_directory = []
    active_requests = BloodRequest.query.filter_by(status='Pending').all()
    
    for h in hospitals:
        h_reqs = [r for r in active_requests if r.hospital == h.username]
        blood_needed = list(set([r.blood_type_needed for r in h_reqs]))
        has_emergency = any(r.is_emergency for r in h_reqs)
        
        # Calculate dynamic urgency
        urgency_level = "HIGH" if has_emergency else "MEDIUM" if len(h_reqs) > 2 else "LOW"
        
        history = hospital_wise.get(h.username, {'count': 0, 'last_date': None})
        
        # Calculate Trust Score (mocked dynamic)
        h_total_apps = len([d for d in donations if d.hospital_name == h.username])
        h_approval_rate = int((history['count'] / h_total_apps) * 100) if h_total_apps > 0 else 100
        trust_score = min(100, 70 + (history['count'] * 10))
        if h_approval_rate < 50: trust_score -= 20
        
        # Distance mock (randomized based on length of name for stability)
        distance = f"{(len(h.username) % 15) + 1}.2 km"
        
        is_trusted = history['count'] > 2 and h_approval_rate >= 80

        hd_obj = {
            'hospital': h,
            'blood_groups_needed': blood_needed,
            'has_emergency': has_emergency,
            'urgency_level': urgency_level,
            'times_donated': history['count'],
            'last_donation': history['last_date'],
            'trust_score': trust_score,
            'distance': distance,
            'is_trusted': is_trusted,
            'approval_rate': h_approval_rate
        }
        
        # AI Match Score
        match_score = 0
        if current_user.blood_type in blood_needed: match_score += 50
        if has_emergency: match_score += 30
        if is_trusted: match_score += 20
        hd_obj['match_score'] = match_score
        
        hospital_directory.append(hd_obj)
        
    # Sort for AI Recommender
    recommended_hospitals = sorted([h for h in hospital_directory if h['match_score'] > 0], key=lambda x: x['match_score'], reverse=True)[:3]

    # 6. PATIENT-LEVEL MATCHING
    patients_you_can_help = []
    for req in active_requests:
        if is_compatible(current_user.blood_type, req.blood_type_needed):
            req_urgency = "HIGH" if req.is_emergency else "MEDIUM" if req.units_required > 2 else "LOW"
            patients_you_can_help.append({
                'id': req.id,
                'name': req.patient_name,
                'blood': req.blood_type_needed,
                'urgency': req_urgency,
                'hospital': req.hospital,
                'time_remaining': "0-6 Hours" if req.is_emergency else "6-24 Hours"
            })
    
    # 8. AI SMART INSIGHTS
    rare_donor_insight = f"You are a rare donor ({current_user.blood_type}). Your donation has high impact." if current_user.blood_type in ['AB-', 'B-', 'O-'] else ""
    urgent_hospitals_count = len([h for h in hospital_directory if h['urgency_level'] == 'HIGH'])
    hospitals_insight = f"{urgent_hospitals_count} hospitals near you need your blood urgently." if urgent_hospitals_count > 0 else "Hospitals currently have stable stock."
    smart_insights = {
        'rare_donor': rare_donor_insight,
        'urgent_hospitals': hospitals_insight,
        'lives_saved': f"You have saved approximately {lives_saved} lives."
    }
    return render_template('dashboard.html', 
                           donations=donations, records=records, 
                           is_eligible=is_eligible, wait_days=wait_days, 
                           unfit_reason=unfit_reason, next_eligible_date=next_eligible_date,
                           stats=stats, badges=badges,
                           hospital_wise=hospital_wise, emergency_requests=emergency_requests,
                           broadcasts=broadcasts, hospital_directory=hospital_directory,
                           recommended_hospitals=recommended_hospitals, datetime=datetime,
                           patients_you_can_help=patients_you_can_help, smart_insights=smart_insights)

@main.route('/upload_health_record', methods=['POST'])
@login_required
@role_required('donor')
def upload_health_record():
    if 'report' not in request.files: return redirect(url_for('main.dashboard'))
    file = request.files['report']
    notes = request.form.get('medical_notes', '')
    if file.filename != '':
        filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        record = HealthRecord(user_id=current_user.id, report_file_path=filename, medical_notes=notes)
        db.session.add(record)
        db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/apply_donation', methods=['POST'])
@login_required
@role_required('donor')
def log_donation():
    hospital_name = request.form.get('hospital_name')
    
    # Backend Integrity Rule: Prevent if Not Eligible
    donations = DonationHistory.query.filter_by(user_id=current_user.id).order_by(DonationHistory.donation_date.desc()).all()
    completed_donations = [d for d in donations if d.status == 'Completed']
    if completed_donations:
        days_since_last = (datetime.utcnow() - completed_donations[0].donation_date).days
        if days_since_last < 90:
            flash("You are not eligible to donate yet. (Minimum 90 days required).", "danger")
            return redirect(url_for('main.dashboard'))
            
    latest_record = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.uploaded_on.desc()).first()
    if not latest_record:
        flash("You must upload a health report before applying.", "warning")
        return redirect(url_for('main.dashboard'))

    # Prevent duplicate pending applications at the same hospital
    existing = DonationHistory.query.filter_by(user_id=current_user.id, hospital_name=hospital_name, status='Pending Approval').first()
    if existing:
        flash("You already have a pending application at this hospital.", "warning")
        return redirect(url_for('main.dashboard'))

    new_donation = DonationHistory(user_id=current_user.id, hospital_name=hospital_name, status='Pending Approval')
    audit = AuditLog(user_id=current_user.id, action=f"Applied to donate at {hospital_name}")
    db.session.add_all([new_donation, audit])
    db.session.commit()
    flash(f"Application sent successfully to {hospital_name}!", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/cancel_application/<int:donation_id>', methods=['POST'])
@login_required
@role_required('donor')
def cancel_application(donation_id):
    application = DonationHistory.query.get_or_404(donation_id)
    if application.user_id != current_user.id or application.status != 'Pending Approval':
        return redirect(url_for('main.dashboard'))
        
    db.session.delete(application)
    audit = AuditLog(user_id=current_user.id, action=f"Canceled application at {application.hospital_name}")
    db.session.add(audit)
    db.session.commit()
    flash("Application canceled.", "info")
    return redirect(url_for('main.dashboard'))

@main.route('/request_blood', methods=['POST'])
@login_required
@role_required('hospital')
@limiter.limit("10 per minute")
def request_blood():
    patient_name = request.form.get('patient_name')
    doctor_reference = request.form.get('doctor_reference')
    age = request.form.get('age')
    diagnosis = request.form.get('diagnosis')
    units_required = request.form.get('units_required', 1)
    hospital = current_user.username
    urgency = request.form.get('urgency')
    blood_type_needed = request.form.get('blood_type')
    is_emergency = request.form.get('is_emergency') == 'on'
    
    # Handle report upload
    report_file_path = None
    if 'patient_report' in request.files:
        file = request.files['patient_report']
        if file.filename != '':
            filename = secure_filename(f"req_{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            report_file_path = filename

    new_request = BloodRequest(
        user_id=current_user.id, patient_name=patient_name, doctor_reference=doctor_reference,
        age=age, diagnosis=diagnosis, units_required=units_required, report_file_path=report_file_path,
        blood_type_needed=blood_type_needed, urgency=urgency, hospital=hospital, is_emergency=is_emergency
    )
    db.session.add(new_request)
    
    if is_emergency:
        msg = BroadcastMessage(title=f"EMERGENCY: {blood_type_needed} needed at {hospital}",
                               description=f"Immediate need for {units_required} unit(s) of {blood_type_needed}. Diagnosis: {diagnosis}",
                               priority='Emergency', sender_name=hospital)
        db.session.add(msg)
        flash(f"CRITICAL ALERT: Emergency request broadcasted.", "danger")
        
    audit = AuditLog(user_id=current_user.id, action=f"Created {'EMERGENCY ' if is_emergency else ''}Request for {blood_type_needed}")
    db.session.add(audit)
    db.session.commit()
    
    return redirect(url_for('main.dashboard'))

@main.route('/hospital/verify_donor/<int:donation_id>', methods=['POST'])
@login_required
@role_required('hospital')
def verify_donor(donation_id):
    donation = DonationHistory.query.get_or_404(donation_id)
    if donation.hospital_name != current_user.username: return jsonify({"error": "Unauthorized"}), 403
    donation.status = request.form.get('status')
    donation.health_notes = request.form.get('notes', '')
    audit = AuditLog(user_id=current_user.id, action=f"Verified donor {donation.user_id} as {donation.status}")
    db.session.add(audit)
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/hospital/assign_donor/<int:request_id>', methods=['POST'])
@login_required
@role_required('hospital')
def assign_donor(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    if req.user_id != current_user.id and req.accepting_hospital != current_user.username:
        return jsonify({"error": "Unauthorized"}), 403
    req.assigned_donor_id = request.form.get('donor_id')
    req.status = 'Assigned'
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/hospital/accept_request/<int:request_id>', methods=['POST'])
@login_required
@role_required('hospital')
def accept_request(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    if req.status != 'Pending': return redirect(url_for('main.dashboard'))
    req.status = 'Accepted'
    req.accepting_hospital = current_user.username
    
    audit = AuditLog(user_id=current_user.id, action=f"Accepted cross-hospital request #{request_id} from {req.hospital}")
    db.session.add(audit)
    db.session.commit()
    flash(f"You have accepted the request for {req.patient_name} from {req.hospital}.", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/hospital/confirm_donation/<int:donation_id>')
@login_required
@role_required('hospital')
def confirm_donation(donation_id):
    donation = DonationHistory.query.get_or_404(donation_id)
    if donation.hospital_name != current_user.username: return jsonify({"error": "Unauthorized"}), 403
    donation.status = 'Completed'
    donation.donation_date = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/fulfill/<int:request_id>')
@login_required
@role_required('hospital', 'admin')
def fulfill_request(request_id):
    req = BloodRequest.query.get_or_404(request_id)
    if req.user_id == current_user.id or req.accepting_hospital == current_user.username or current_user.role == 'admin':
        req.status = 'Fulfilled'
        audit = AuditLog(user_id=current_user.id, action=f"Marked request {request_id} as Fulfilled")
        db.session.add(audit)
        db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/broadcast', methods=['POST'])
@login_required
@role_required('hospital', 'admin')
def send_broadcast():
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority')
    
    msg = BroadcastMessage(title=title, description=description, priority=priority, sender_name=current_user.username)
    db.session.add(msg)
    
    audit = AuditLog(user_id=current_user.id, action=f"Sent {priority} broadcast: {title}")
    db.session.add(audit)
    db.session.commit()
    flash("Broadcast message sent successfully to all hospitals.", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/toggle_availability', methods=['POST'])
@login_required
@role_required('donor')
def toggle_availability():
    current_user.is_available = not current_user.is_available
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    users = User.query.all()
    requests = BloodRequest.query.all()
    donations = DonationHistory.query.all()
    audits = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    analytics = {
        "total_donations": DonationHistory.query.filter_by(status='Completed').count(),
        "active_donors": User.query.filter_by(role='donor', is_available=True).count(),
        "fulfilled_requests": BloodRequest.query.filter_by(status='Fulfilled').count(),
        "total_hospitals": User.query.filter_by(role='hospital').count()
    }
    return render_template('admin_dashboard.html', users=users, requests=requests, donations=donations, analytics=analytics, audits=audits)

@main.route('/admin/backup')
@login_required
@role_required('admin')
@limiter.limit("1 per hour")
def backup_db():
    try:
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        shutil.copy2(db_path, db_path + f".backup_{int(datetime.utcnow().timestamp())}")
        flash("Database backed up successfully.", "success")
    except Exception as e:
        flash(f"Backup failed: {str(e)}", "danger")
    return redirect(url_for('main.admin_dashboard'))
