from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
	r = requests.get('https://www.reddit.com/r/all/new/.json', headers = {'User-agent': 'your bot 0.1'})
	print(r.json())
	return "yo"