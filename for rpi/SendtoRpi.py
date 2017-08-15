import json, requests

url = 'http://127.0.0.1:8000/carlist/'
"""
params = dict(TEJ123
    origin='Chicago,IL',
    destination='Los+Angeles,CA',
    waypoints='Joplin,MO|Oklahoma+City,OK',
    sensor='false'

)
THIS IS FOR CAR STATUS
"""
example = 'http://127.0.0.1:8000/auth/'

#data = requests.put(url=url,params)

def _get():
	data = requests.get(url=url, params=params) #params=params for parameter before getting
	binary = data.content
	output = json.loads(binary)

	# test to see if the request was valid
	print (output['car_stat'])
	
def _post():
	payload= {
		'username':'admin',
		'password' : 'admin1234'
	}
	response = requests.post(url=example, data=payload)
	print (response.json())
	print (response.json()['user'])
_post()