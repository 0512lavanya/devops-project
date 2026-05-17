import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_ui = """            <!-- DONOR VIEW -->
            <div style="max-width: 600px; margin: 0 auto; background: rgba(15, 23, 42, 0.9); padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); font-family: monospace; color: #e2e8f0; font-size: 1rem; line-height: 1.5;">
                
                <h2 style="text-align: center; color: #3b82f6; margin-bottom: 2rem;">💧 VitalDrop</h2>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <div>👤 User: {{ current_user.username }}</div>
                    <div>🔓 <a href="{{ url_for('main.logout') }}" style="color: #ef4444; text-decoration: none;">Logout</a></div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #ef4444; margin-top: 0;">🩸 DONOR DASHBOARD</h3>
                    
                    {% if is_eligible %}
                        <div style="color: #10b981; font-weight: bold; margin-bottom: 0.5rem;">✅ Status: Eligible to Donate</div>
                        <div style="margin-bottom: 1rem;">You meet all medical and interval requirements.</div>
                    {% else %}
                        <div style="color: #ef4444; font-weight: bold; margin-bottom: 0.5rem;">❌ Status: Temporarily Ineligible</div>
                        <div style="margin-bottom: 1rem;">{{ unfit_reason }}</div>
                    {% endif %}
                    <div style="margin-bottom: 1rem;">📅 Next Eligible Date: {{ next_eligible_date.strftime('%B %d, %Y') }}</div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #f59e0b; margin-top: 0;">🚀 LIVE AVAILABILITY</h3>
                    <form action="{{ url_for('main.toggle_availability') }}" method="POST" style="margin-bottom: 1rem; display: inline-block;">
                        <button type="submit" style="background: transparent; border: 1px solid #94a3b8; color: #fff; padding: 0.2rem 0.5rem; cursor: pointer;">[Toggle Switch]</button>
                    </form>
                    {% if current_user.is_available %}
                        <div style="color: #10b981; font-weight: bold; margin-bottom: 0.5rem;">✅ Available for Emergency Donations</div>
                    {% else %}
                        <div style="color: #94a3b8; font-weight: bold; margin-bottom: 0.5rem;">⏸️ Not Available for Emergency Donations</div>
                    {% endif %}
                    <div style="color: #94a3b8;">When enabled, your profile is prioritized for urgent hospital requests.</div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #3b82f6; margin-top: 0;">🏥 HOSPITAL MATCHING</h3>
                    <div style="margin-bottom: 0.5rem;">Blood Group: {{ current_user.blood_type }}</div>
                    <div style="margin-bottom: 1rem;">Location: {{ current_user.location }}</div>
                    
                    <div style="margin-bottom: 0.5rem;">🔍 Nearby Requests:</div>
                    {% if emergency_requests %}
                        {% for req in emergency_requests[:1] %}
                            <ul style="margin: 0; padding-left: 1.5rem;">
                                <li style="color: #fca5a5;">Emergency: Needed Now</li>
                                <li style="color: #fca5a5;">Distance: &lt; 10 km</li>
                            </ul>
                        {% endfor %}
                    {% else %}
                        <ul style="margin: 0; padding-left: 1.5rem; color: #94a3b8;">
                            <li>No urgent matches nearby</li>
                        </ul>
                    {% endif %}
                    
                    <div style="margin-top: 1rem;">
                        <a href="#" style="color: #3b82f6; text-decoration: none;">[View Hospitals]</a>
                    </div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #8b5cf6; margin-top: 0;">📊 DONATION ANALYTICS</h3>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 0.5rem;">
                        <div>Total Donations:</div><div>{{ stats.total_donations }}</div>
                        <div>Lives Potentially Saved:</div><div>{{ stats.lives_saved }}</div>
                        <div>Approval Rate:</div><div>{{ stats.approval_rate }}%</div>
                        <div>Emergency Responses:</div><div>{{ stats.emergency_donations }}</div>
                    </div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #f59e0b; margin-top: 0;">🏆 GAMIFICATION</h3>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <div style="display: grid; grid-template-columns: 2fr 1fr;">
                            <span>🥉 First Donation</span><span>[{{ (stats.total_donations >= 1) and '100' or '0' }}%]</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 2fr 1fr;">
                            <span>🥈 Life Saver (5)</span><span>[{{ (stats.total_donations / 5 * 100)|int if stats.total_donations < 5 else 100 }}%]</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 2fr 1fr;">
                            <span>🥇 Super Donor (10+)</span><span>[{{ (stats.total_donations / 10 * 100)|int if stats.total_donations < 10 else 100 }}%]</span>
                        </div>
                    </div>
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #10b981; margin-top: 0;">📈 DONATION TIMELINE</h3>
                    {% if donations %}
                        <ul style="margin: 0; padding-left: 1.5rem;">
                        {% for d in donations[:3] %}
                            <li>{{ d.donation_date.strftime('%B %d, %Y') }} - {{ d.hospital_name }}</li>
                        {% endfor %}
                        </ul>
                    {% else %}
                        <div style="margin-bottom: 0.5rem;">No donations yet.</div>
                        <div style="color: #94a3b8;">(Start your first donation to unlock insights)</div>
                    {% endif %}
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #3b82f6; margin-top: 0;">🧾 HEALTH RECORD VAULT</h3>
                    
                    <form action="{{ url_for('main.upload_health_record') }}" method="POST" enctype="multipart/form-data" style="margin-bottom: 1.5rem;">
                        <div style="margin-bottom: 0.5rem;">Upload Medical Reports:</div>
                        <input type="file" name="report" style="margin-bottom: 1rem; width: 100%; font-family: monospace;">
                        
                        <div style="margin-bottom: 0.5rem;">Medical Notes:</div>
                        <textarea name="medical_notes" placeholder="[ Enter conditions / remarks ]" style="width: 100%; padding: 0.5rem; background: transparent; color: #fff; border: 1px solid #475569; margin-bottom: 1rem; font-family: monospace;"></textarea>
                        
                        <button type="submit" style="background: transparent; border: none; color: #10b981; cursor: pointer; text-align: left; padding: 0; font-family: monospace; font-size: 1rem;">🔒 Secure Upload + Auto Verification</button>
                    </form>

                    <div style="margin-bottom: 0.5rem;">Recent Records:</div>
                    {% if records %}
                        {% for rec in records %}
                            <div style="color: #10b981; margin-bottom: 0.2rem;">✔ Verified ({{ rec.uploaded_on.strftime('%B %d, %Y') }})</div>
                        {% endfor %}
                    {% else %}
                        <div style="color: #94a3b8;">No records found.</div>
                    {% endif %}
                </div>
                <div style="border-bottom: 1px dashed #475569; margin-bottom: 1rem;"></div>

                <div>
                    <h3 style="color: #fca5a5; margin-top: 0;">⚡ QUICK ACTIONS</h3>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <a href="#" style="color: #e2e8f0; text-decoration: none;">[ Donate Now ]</a>
                        <a href="#" style="color: #e2e8f0; text-decoration: none;">[ Find Nearby Camps ]</a>
                        <a href="#" style="color: #e2e8f0; text-decoration: none;">[ Update Profile ]</a>
                        <form action="{{ url_for('main.toggle_availability') }}" method="POST" style="margin: 0;">
                            <button type="submit" style="background: transparent; border: none; color: #ef4444; text-decoration: none; font-weight: bold; padding: 0; cursor: pointer; font-family: monospace; font-size: 1rem;">[ Emergency Mode {% if current_user.is_available %}ON{% else %}OFF{% endif %} ]</button>
                        </form>
                    </div>
                </div>

            </div>"""

start_idx = content.find('<!-- DONOR VIEW -->')
end_idx = content.find('{% endif %}', start_idx) + len('{% endif %}')

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_ui + '\n        ' + content[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully replaced.")
else:
    print("Could not find start or end index.")
