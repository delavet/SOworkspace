import flask

from flask import Flask, request, jsonify
from util.HOMURA_service import HOMURAservice
from util.config import JAVADOC_GLOBAL_NAME

app = Flask(__name__)

HOMURA_services = {
    JAVADOC_GLOBAL_NAME: HOMURAservice(JAVADOC_GLOBAL_NAME)
}


def after_request(response):
   response.headers['Access-Control-Allow-Origin'] = '*'
   response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
   response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
   return response

app.after_request(after_request)


@app.route('/api/hello')
def hello():
    response = flask.make_response("hello lex")
    return response


@app.route('/api/getLearnSections/<doc_name>', methods = ["GET"])
def get_learning_sections(doc_name):
    '''
    返回json：
    {
        "success" : True,
        "data" : [
            {
                "section_id" : "1",
                "apis": ["api1", "api2" ...],
                "thread_info": {
                    "Id": 1,
                    "Title": "test",
                    "Tags": "<test><test>"
                }
            },...
        ]
    }
    '''
    limit = int(request.args.get("limit", default=0))
    page = int(request.args.get("page", default=0))
    start_index = page * limit
    end_index = start_index + limit
    data = []
    if start_index >= len(HOMURA_services[doc_name].community_ids):
        data = []
    else:
        for i in range(start_index, min(end_index, len(HOMURA_services[doc_name].community_ids))):
            data.append(HOMURA_services[doc_name].get_community_recommend_info(
                HOMURA_services[doc_name].community_ids[i]))
    ret = {
        "success" : True,
        "data" : data
    }
    response = flask.make_response(jsonify(ret))
    return response



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
