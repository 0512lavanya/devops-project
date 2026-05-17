import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Smart Insights Box (Right under the top banner)
insights_html = """
            <!-- 8. SMART AI INSIGHTS -->
            <div style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(139,92,246,0.3); padding: 1.2rem; border-radius: 12px; margin-bottom: 2rem; display: flex; flex-direction: column; gap: 0.8rem;">
                <h3 style="margin: 0; color: #a78bfa; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🧠</span> VitalDrop AI Insights
                </h3>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
                    {% if smart_insights.rare_donor %}
                        <div style="background: rgba(15,23,42,0.6); padding: 0.6rem 1rem; border-radius: 8px; color: #cbd5e1; font-size: 0.9rem; border-left: 3px solid #f43f5e;">
                            {{ smart_insights.rare_donor }}
                        </div>
                    {% endif %}
                    <div style="background: rgba(15,23,42,0.6); padding: 0.6rem 1rem; border-radius: 8px; color: #cbd5e1; font-size: 0.9rem; border-left: 3px solid #f59e0b;">
                        {{ smart_insights.urgent_hospitals }}
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 0.6rem 1rem; border-radius: 8px; color: #cbd5e1; font-size: 0.9rem; border-left: 3px solid #10b981;">
                        {{ smart_insights.lives_saved }}
                    </div>
                </div>
            </div>
"""
# Inject right before the premium-grid
if '<div class="premium-grid">' in content:
    content = content.replace('<div class="premium-grid">', insights_html + '\n            <div class="premium-grid">')


# 2. Patients You Can Help
patients_html = """
                <!-- PATIENTS YOU CAN HELP -->
                <div class="premium-card" style="grid-column: 1 / -1; border-top: 3px solid #f43f5e;">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">🚨</span>
                        <h3 class="card-title">Patients You Can Help</h3>
                    </div>
                    
                    {% if patients_you_can_help %}
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
                            {% for p in patients_you_can_help %}
                                <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 12px; display: flex; flex-direction: column; gap: 0.8rem;">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <div style="font-weight: 600; color: #f8fafc; font-size: 1.1rem;">{{ p.name }}</div>
                                        <div style="background: {% if p.urgency == 'HIGH' %}#ef4444{% elif p.urgency == 'MEDIUM' %}#f59e0b{% else %}#10b981{% endif %}; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">
                                            {{ p.urgency }}
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
                                        <div style="color: #94a3b8;">Needs: <strong style="color: #f43f5e; font-size: 1rem;">{{ p.blood }}</strong></div>
                                        <div style="color: #94a3b8;">Time: <strong style="color: #cbd5e1;">{{ p.time_remaining }}</strong></div>
                                    </div>
                                    <div style="font-size: 0.85rem; color: #94a3b8; display: flex; align-items: center; gap: 0.4rem;">
                                        <span>🏥</span> {{ p.hospital }}
                                    </div>
                                    <button class="action-btn danger" style="margin: 0; margin-top: 0.5rem; justify-content: center; font-size: 0.85rem; padding: 0.6rem;">Donate to This Patient</button>
                                </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <div style="background: rgba(15,23,42,0.4); padding: 1.5rem; border-radius: 8px; text-align: center; color: #94a3b8; font-size: 0.9rem;">
                            No compatible patients currently match your blood type.
                        </div>
                    {% endif %}
                </div>
"""
# Inject before Analytics
if '<!-- ANALYTICS -->' in content:
    content = content.replace('<!-- ANALYTICS -->', patients_html + '\n                <!-- ANALYTICS -->')


# 3. Map Integration Mock
map_html = """
                <!-- MAP INTEGRATION -->
                <div class="premium-card" style="grid-column: 1 / -1;">
                    <div class="card-header" style="display: flex; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 0.8rem;">
                            <span style="font-size: 1.5rem;">🗺️</span>
                            <h3 class="card-title">Live Hospital Map</h3>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <select class="form-input" style="padding: 0.3rem 0.5rem; font-size: 0.8rem; background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 4px;">
                                <option value="all">Distance: All</option>
                                <option value="5">Within 5 km</option>
                                <option value="10">Within 10 km</option>
                            </select>
                            <select class="form-input" style="padding: 0.3rem 0.5rem; font-size: 0.8rem; background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 4px;">
                                <option value="all">Priority: All</option>
                                <option value="high">HIGH Only</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="width: 100%; height: 300px; background: url('https://raw.githubusercontent.com/googlemaps/js-samples/main/dist/samples/advanced-markers-simple/docs/img/advanced-markers-simple.png') center/cover; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6);"></div>
                        <div style="position: relative; z-index: 10; background: rgba(15,23,42,0.8); padding: 1rem 2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-align: center; backdrop-filter: blur(4px);">
                            <div style="font-size: 1.2rem; color: #f8fafc; margin-bottom: 0.5rem;">📍 Interactive Map Active</div>
                            <div style="font-size: 0.85rem; color: #94a3b8;">Displaying real-time locations of matching hospitals.</div>
                            <button style="margin-top: 1rem; background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; font-weight: 500; cursor: pointer;">Expand Map</button>
                        </div>
                    </div>
                </div>
"""
# Inject before Quick Actions
if '<!-- QUICK ACTIONS -->' in content:
    content = content.replace('<!-- QUICK ACTIONS -->', map_html + '\n                <!-- QUICK ACTIONS -->')


with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("dashboard.html successfully patched with new requested features.")
