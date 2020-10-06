"""Minimal example redirector


 FLASK_APP=simple.py flask run -p 8001 -h localhost


"""
from flask import Flask, request

app=Flask(__name__)

@app.route('/',  methods=['POST'])
def getURL():
    if request.method == 'POST':
        data= request.json
        print(data)
    return {'url': 'http://localhost:8001/hello'}

@app.route('/hello')
def hello():
   return 'Hello!'


