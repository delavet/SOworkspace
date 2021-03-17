from flask import Flask
import flask

app = Flask(__name__)


def after_request(response):
   response.headers['Access-Control-Allow-Origin'] = '*'
   response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
   response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
   return response

app.after_request(after_request)


@app.route('/api/hello')
def hello():
    response = flask.make_response("hello")
    
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
