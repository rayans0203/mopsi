#tuto : http://docs.python-requests.org/en/master/user/quickstart/

import requests

r = requests.post('http://127.0.0.1:8000/userInterface/pricer',{'Stock':'value'})

r = requests.get('http://127.0.0.1:8000/userInterface/pricer', "10")
