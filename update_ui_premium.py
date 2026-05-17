import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_ui = """            <!-- PREMIUM DONOR VIEW -->
            
            <style>
                .premium-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
                .premium-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 1.5rem; transition: transform 0.3s ease, box-shadow 0.3s ease; }
                .premium-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); }
                .card-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.8rem; }
                .card-title { margin: 0; font-size: 1.1rem; font-weight: 600; color: #f8fafc; display: flex; align-items: center; gap: 0.5rem; }
                
                .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
                .stat-box { background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.02); }
                .stat-value { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.3rem; }
                
                .badge-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; margin-bottom: 0.4rem; color: #cbd5e1; }
                .progress-bar { width: 100%; height: 8px; background: rgba(255,255,255,0.05); border-radius: 99px; overflow: hidden; margin-bottom: 1.2rem; }
                .progress-fill { height: 100%; background: linear-gradient(90deg, #10b981, #34d399); border-radius: 99px; transition: width 1s ease-in-out; }
                
                .action-btn { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.2rem; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; color: #eff6ff; text-decoration: none; font-weight: 500; transition: all 0.2s ease; margin-bottom: 0.8rem; }
                .action-btn:hover { background: rgba(59, 130, 246, 0.2); transform: translateX(5px); }
                .action-btn.danger { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); color: #fef2f2; }
                .action-btn.danger:hover { background: rgba(239, 68, 68, 0.2); }
                
                .toggle-switch { appearance: none; width: 50px; height: 26px; background: #475569; border-radius: 99px; position: relative; cursor: pointer; outline: none; transition: background 0.3s; }
                .toggle-switch::after { content: ''; position: absolute; top: 2px; left: 2px; width: 22px; height: 22px; background: white; border-radius: 50%; transition: transform 0.3s; }
                .toggle-switch:checked { background: #10b981; }
                .toggle-switch:checked::after { transform: translateX(24px); }
            </style>

            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(30,41,59,0.8); backdrop-filter: blur(20px); padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2rem;">
                <div>
                    <h2 style="margin: 0; color: #f8fafc; font-size: 1.5rem; display: flex; align-items: center; gap: 0.8rem;">
                        <span style="font-size: 2rem;">💧</span> VitalDrop
                    </h2>
                </div>
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.05); padding: 0.5rem 1rem; border-radius: 99px;">
                        <span style="background: linear-gradient(135deg, #60a5fa, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">👤 {{ current_user.username }}</span>
                    </div>
                    <a href="{{ url_for('main.logout') }}" style="color: #f87171; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 0.4rem; transition: color 0.2s;">
                        <span>🔓</span> Logout
                    </a>
                </div>
            </div>

            <!-- ELIGIBILITY & AVAILABILITY BANNER -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
                <div class="premium-card" style="border-left: 4px solid {% if is_eligible %}#10b981{% else %}#ef4444{% endif %}; background: linear-gradient(to right, {% if is_eligible %}rgba(16,185,129,0.1){% else %}rgba(239,68,68,0.1){% endif %}, rgba(30,41,59,0.7));">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.4rem; color: {% if is_eligible %}#34d399{% else %}#f87171{% endif %}; display: flex; align-items: center; gap: 0.5rem;">
                                {% if is_eligible %}✅ Eligible to Donate{% else %}❌ Temporarily Ineligible{% endif %}
                            </h3>
                            <p style="color: #cbd5e1; margin: 0 0 1rem 0; font-size: 0.95rem;">
                                {% if is_eligible %}You meet all medical and interval requirements.{% else %}{{ unfit_reason }}{% endif %}
                            </p>
                            <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(15,23,42,0.5); padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                                <span style="font-size: 1.2rem;">📅</span>
                                <div>
                                    <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Next Eligible Date</div>
                                    <div style="color: #f8fafc; font-weight: 600;">{{ next_eligible_date.strftime('%B %d, %Y') }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="premium-card" style="display: flex; flex-direction: column; justify-content: center;">
                    <div class="card-header" style="border:none; margin-bottom: 0.5rem;">
                        <h3 class="card-title">🚀 Live Availability</h3>
                    </div>
                    <form action="{{ url_for('main.toggle_availability') }}" method="POST" style="margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between; background: rgba(15,23,42,0.5); padding: 0.8rem 1rem; border-radius: 12px;">
                        <div style="font-weight: 500; color: {% if current_user.is_available %}#10b981{% else %}#94a3b8{% endif %};">
                            {% if current_user.is_available %}Available for Emergency{% else %}Currently Unavailable{% endif %}
                        </div>
                        <button type="submit" style="background:transparent; border:none; padding:0; margin:0;">
                            <input type="checkbox" class="toggle-switch" {% if current_user.is_available %}checked{% endif %} onclick="this.form.submit()">
                        </button>
                    </form>
                    <p style="font-size: 0.8rem; color: #94a3b8; margin: 0; line-height: 1.4;">When enabled, your profile is prioritized for urgent hospital requests.</p>
                </div>
            </div>

            <div class="premium-grid">
                <!-- HOSPITAL MATCHING -->
                <div class="premium-card">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">🏥</span>
                        <h3 class="card-title">Hospital Matching</h3>
                    </div>
                    
                    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="flex: 1; background: rgba(15,23,42,0.5); padding: 0.8rem; border-radius: 8px; text-align: center;">
                            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Blood Group</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #ef4444;">{{ current_user.blood_type }}</div>
                        </div>
                        <div style="flex: 2; background: rgba(15,23,42,0.5); padding: 0.8rem; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Location</div>
                            <div style="font-size: 1.1rem; color: #f8fafc; font-weight: 500; text-transform: capitalize;">{{ current_user.location }}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 1.5rem;">
                        <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span>🔍</span> Nearby Requests
                        </div>
                        {% if emergency_requests %}
                            {% for req in emergency_requests[:1] %}
                                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 8px; position: relative; overflow: hidden;">
                                    <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #ef4444;"></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                                        <strong style="color: #fca5a5;">Emergency: Needed Now</strong>
                                        <span style="color: #ef4444; font-size: 0.8rem; font-weight: bold;" class="pulse">● LIVE</span>
                                    </div>
                                    <div style="font-size: 0.85rem; color: #f8fafc;">Distance: &lt; 10 km</div>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div style="background: rgba(15,23,42,0.4); padding: 1rem; border-radius: 8px; text-align: center; color: #94a3b8; font-size: 0.9rem;">
                                No urgent matches nearby
                            </div>
                        {% endif %}
                    </div>

                    <a href="#" style="display: block; text-align: center; color: #60a5fa; text-decoration: none; font-size: 0.9rem; font-weight: 500; padding: 0.8rem; background: rgba(59,130,246,0.1); border-radius: 8px; transition: background 0.2s;">
                        View All Hospitals →
                    </a>
                </div>

                <!-- ANALYTICS -->
                <div class="premium-card">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">📊</span>
                        <h3 class="card-title">Donation Analytics</h3>
                    </div>
                    
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text;">{{ stats.total_donations }}</div>
                            <div class="stat-label">Total Donations</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text;">{{ stats.lives_saved }}</div>
                            <div class="stat-label">Lives Saved</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa); -webkit-background-clip: text;">{{ stats.approval_rate }}%</div>
                            <div class="stat-label">Approval Rate</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text;">{{ stats.emergency_donations }}</div>
                            <div class="stat-label">Emergencies</div>
                        </div>
                    </div>
                </div>

                <!-- GAMIFICATION -->
                <div class="premium-card">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">🏆</span>
                        <h3 class="card-title">Gamification</h3>
                    </div>
                    
                    <div>
                        <div class="badge-row">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">🥉 First Donation</span>
                            <span style="font-weight: 600; color: #10b981;">{{ (stats.total_donations >= 1) and '100' or '0' }}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ (stats.total_donations >= 1) and '100' or '0' }}%;"></div>
                        </div>

                        <div class="badge-row">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">🥈 Life Saver <span style="font-size: 0.75rem; color: #64748b; background: rgba(255,255,255,0.1); padding: 0.1rem 0.4rem; border-radius: 4px;">5</span></span>
                            <span style="font-weight: 600; color: #10b981;">{{ (stats.total_donations / 5 * 100)|int if stats.total_donations < 5 else 100 }}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ (stats.total_donations / 5 * 100)|int if stats.total_donations < 5 else 100 }}%; background: linear-gradient(90deg, #3b82f6, #60a5fa);"></div>
                        </div>

                        <div class="badge-row">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">🥇 Super Donor <span style="font-size: 0.75rem; color: #64748b; background: rgba(255,255,255,0.1); padding: 0.1rem 0.4rem; border-radius: 4px;">10+</span></span>
                            <span style="font-weight: 600; color: #10b981;">{{ (stats.total_donations / 10 * 100)|int if stats.total_donations < 10 else 100 }}%</span>
                        </div>
                        <div class="progress-bar" style="margin-bottom: 0;">
                            <div class="progress-fill" style="width: {{ (stats.total_donations / 10 * 100)|int if stats.total_donations < 10 else 100 }}%; background: linear-gradient(90deg, #8b5cf6, #a78bfa);"></div>
                        </div>
                    </div>
                </div>

                <!-- DONATION TIMELINE -->
                <div class="premium-card">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">📈</span>
                        <h3 class="card-title">Donation Timeline</h3>
                    </div>
                    
                    <div style="padding-left: 0.5rem; border-left: 2px solid rgba(255,255,255,0.1); margin-left: 0.5rem;">
                    {% if donations %}
                        {% for d in donations[:3] %}
                            <div style="position: relative; margin-bottom: 1.5rem; padding-left: 1rem;">
                                <div style="position: absolute; left: -21px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: #10b981; border: 2px solid #1e293b;"></div>
                                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.2rem;">{{ d.donation_date.strftime('%B %d, %Y') }}</div>
                                <div style="color: #f8fafc; font-weight: 500;">{{ d.hospital_name }}</div>
                            </div>
                        {% endfor %}
                    {% else %}
                        <div style="padding-left: 1rem; color: #94a3b8; font-size: 0.9rem;">
                            <div style="margin-bottom: 0.5rem;">No donations yet.</div>
                            <div style="font-size: 0.8rem; color: #64748b;">Start your first donation to unlock insights.</div>
                        </div>
                    {% endif %}
                    </div>
                </div>

                <!-- HEALTH RECORD VAULT -->
                <div class="premium-card" style="grid-column: 1 / -1;">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">🧾</span>
                        <h3 class="card-title">Health Record Vault</h3>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                        <form action="{{ url_for('main.upload_health_record') }}" method="POST" enctype="multipart/form-data" style="background: rgba(15,23,42,0.5); padding: 1.5rem; border-radius: 12px; border: 1px dashed rgba(255,255,255,0.2);">
                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.5rem;">Upload Medical Reports</label>
                                <input type="file" name="report" style="width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.2); border-radius: 8px; color: #f8fafc; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.1);">
                            </div>
                            
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.5rem;">Medical Notes</label>
                                <textarea name="medical_notes" placeholder="Enter conditions or remarks..." style="width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.2); border-radius: 8px; color: #f8fafc; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.1); min-height: 80px; resize: vertical;"></textarea>
                            </div>
                            
                            <button type="submit" style="width: 100%; background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 1rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: transform 0.2s, box-shadow 0.2s;">
                                <span>🔒</span> Secure Upload + Auto Verification
                            </button>
                        </form>

                        <div>
                            <h4 style="margin: 0 0 1rem 0; color: #cbd5e1; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">Recent Records</h4>
                            {% if records %}
                                <div style="display: flex; flex-direction: column; gap: 0.8rem;">
                                {% for rec in records %}
                                    <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.8rem 1rem; border-radius: 8px;">
                                        <div style="display: flex; align-items: center; gap: 0.6rem;">
                                            <span style="background: #10b981; color: #fff; width: 20px; height: 20px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem;">✔</span>
                                            <span style="color: #f8fafc; font-size: 0.9rem;">Verified Report</span>
                                        </div>
                                        <span style="color: #34d399; font-size: 0.8rem; font-weight: 600;">{{ rec.uploaded_on.strftime('%B %d, %Y') }}</span>
                                    </div>
                                {% endfor %}
                                </div>
                            {% else %}
                                <div style="background: rgba(15,23,42,0.5); padding: 1.5rem; border-radius: 8px; text-align: center; color: #94a3b8; font-size: 0.9rem; border: 1px dashed rgba(255,255,255,0.1);">
                                    No medical records found in your vault.
                                </div>
                            {% endif %}
                        </div>
                    </div>
                </div>

                <!-- QUICK ACTIONS -->
                <div class="premium-card" style="grid-column: 1 / -1; background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9));">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">⚡</span>
                        <h3 class="card-title">Quick Actions</h3>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                        <a href="#" class="action-btn">
                            <span>Donate Now</span>
                            <span>→</span>
                        </a>
                        <a href="#" class="action-btn">
                            <span>Find Nearby Camps</span>
                            <span>→</span>
                        </a>
                        <a href="#" class="action-btn">
                            <span>Update Profile</span>
                            <span>→</span>
                        </a>
                        <form action="{{ url_for('main.toggle_availability') }}" method="POST" style="margin: 0;">
                            <button type="submit" class="action-btn danger" style="width: 100%; border: none; cursor: pointer;">
                                <span>Emergency Mode {% if current_user.is_available %}ON{% else %}OFF{% endif %}</span>
                                <span>🚨</span>
                            </button>
                        </form>
                    </div>
                </div>

            </div>"""

start_idx = content.find('<!-- DONOR VIEW -->')
end_idx = content.rfind('</div>', 0, content.find('{% endif %}', start_idx)) + 6 # Find the end of the previous UI string we inserted

# Actually, the best way to replace is to find "<!-- DONOR VIEW -->" and the very last "</div>" before "{% endif %}" at the end of the file
# Let's read the file again properly, we know what we just inserted.

if start_idx != -1:
    end_tag_idx = content.find('{% endif %}', start_idx)
    content = content[:start_idx] + new_ui + '\n        ' + content[end_tag_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully replaced.")
else:
    print("Could not find start index.")
