from flask import Flask
from flask import current_app
from flask import make_response

app = Flask(__name__)

@app.route('/')
def cookie_insertion():
    resp = make_response('hello')
    resp.set_cookie('username', 'the username',domain='127.0.0.1')
    return resp

if __name__ == '__main__':
    app.run()