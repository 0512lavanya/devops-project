import requests

session = requests.Session()
# Sign up a new user
response = session.post('http://localhost:5000/signup', data={
    'username': 'HospitalTest500',
    'email': 'hosp500@example.com',
    'password': 'password',
    'blood_type': '',
    'location': 'New York',
    'role': 'hospital'
})

response = session.get('http://localhost:5000/dashboard')
print("Dashboard Status Code:", response.status_code)
if response.status_code == 500:
    print(response.text)
