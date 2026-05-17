import sys

def patch_routes():
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the compatibility logic function to inject
    compat_logic = """
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
"""

    # Inject the compat_logic right before "hospitals = User.query.filter_by(role='hospital').all()"
    marker1 = "    hospitals = User.query.filter_by(role='hospital').all()"
    if marker1 in content:
        content = content.replace(marker1, compat_logic + "\n" + marker1)
    
    # Replace urgency calculation
    old_urgency = 'urgency_level = "Critical" if has_emergency else "High" if len(h_reqs) > 2 else "Normal"'
    new_urgency = 'urgency_level = "HIGH" if has_emergency else "MEDIUM" if len(h_reqs) > 2 else "LOW"'
    content = content.replace(old_urgency, new_urgency)

    # After the hospital loop, add patients_you_can_help and smart_insights
    marker2 = "recommended_hospitals.sort(key=lambda x: x['match_score'], reverse=True)"
    
    injections = """
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
"""

    if marker2 in content:
        content = content.replace(marker2, marker2 + "\n" + injections)

    # Now update the render_template call to include the new variables
    old_render = """                           broadcasts=broadcasts, hospital_directory=hospital_directory,
                           recommended_hospitals=recommended_hospitals, datetime=datetime)"""
    new_render = """                           broadcasts=broadcasts, hospital_directory=hospital_directory,
                           recommended_hospitals=recommended_hospitals, datetime=datetime,
                           patients_you_can_help=patients_you_can_help, smart_insights=smart_insights)"""
    content = content.replace(old_render, new_render)

    with open('app/routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("routes.py successfully patched.")

if __name__ == '__main__':
    patch_routes()
