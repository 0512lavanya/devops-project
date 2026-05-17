import requests
import re

session = requests.Session()
# Sign up a new user
response = session.post('http://localhost:5000/signup', data={
    'username': 'HospitalTest123',
    'email': 'hosp@example.com',
    'password': 'password',
    'blood_type': '',
    'location': 'New York',
    'role': 'hospital'
})

print("Status Code:", response.status_code)
if response.status_code == 500:
    print(response.text)
else:
    # Try getting dashboard
    response = session.get('http://localhost:5000/dashboard')
    print("Dashboard Status Code:", response.status_code)
    if response.status_code == 500:
        match = re.search(r'(Traceback \(most recent call last\):.*?)(?:\n\n|\Z)', response.text, re.DOTALL | re.IGNORECASE)
        if match:
            print(match.group(1))
        else:
            print("Could not parse traceback, printing all:")
            print(response.text[:2000])
