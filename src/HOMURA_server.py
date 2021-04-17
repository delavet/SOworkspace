import flask

from flask import Flask, request, jsonify
from util.HOMURA_service import HOMURAservice
from util.apidoc_search.api_search_service import ApiSearchService
from util.config import JAVADOC_GLOBAL_NAME
from util.utils import get_api_qualified_name_from_entity_id

app = Flask(__name__)

HOMURA_services = {
    JAVADOC_GLOBAL_NAME: HOMURAservice(JAVADOC_GLOBAL_NAME)
}

SEARCH_services = {
    JAVADOC_GLOBAL_NAME: ApiSearchService(JAVADOC_GLOBAL_NAME)
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


@app.route('/api/getCommunitySubmap/<doc_name>', methods = ['GET'])
def get_community_submap(doc_name):
    section_id = request.args.get("sectionId", default=-1)
    api_id = request.args.get("apiId", default=None)
    ret = {
        'success': True,
        'data': []
    }
    try:
        if section_id != -1:
            if api_id is None:
                ret['data'] = HOMURA_services[doc_name].get_community_submap_by_section(
                    section_id)
            else:
                ret['data'] = HOMURA_services[doc_name].get_community_submap_by_api(
                    api_id, section_id)
        else:
            ret['data'] = HOMURA_services[doc_name].get_community_submap_by_api(
                api_id)
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/getConceptSubmap/<doc_name>', methods = ['GET'])
def get_concept_submap(doc_name):
    api_id = request.args.get("apiId", default=None)
    ret = {
        'success': True,
        'data': []
    }
    ret['data'] = HOMURA_services[doc_name].get_concept_submap_by_api(
        api_id)
    try:
        pass
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/getAPIDescription/<doc_name>', methods=['GET'])
def get_api_description(doc_name):
    api_id = request.args.get("apiId", default=None)
    ret = {
        'success': True,
        'data': ''
    }
    try:
        api_name, api_html = HOMURA_services[doc_name].get_api_description_html(api_id)
        ret['data'] = {
            'api_name': api_name,
            'api_html': api_html
        }
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/getThreadInfo/<doc_name>', methods=['GET'])
def get_thread_info(doc_name):
    api_id = request.args.get("apiId", default=None)
    page = int(request.args.get("page", default=0))
    limit = int(request.args.get("limit", default=20))
    ret = {
        'success': True,
        'data': []
    }
    try:
        thread_info = HOMURA_services[doc_name].get_thread_infos_by_api_local(api_id, page, limit)
        ret['data'] = thread_info
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/getThreadHtml/<doc_name>', methods=['GET'])
def get_thread_html(doc_name):
    thread_id = str(request.args.get("threadId", default="9395808"))
    ret = {
        'success': True,
        'data': []
    }
    try:
        data = HOMURA_services[doc_name].get_thread_html(thread_id)
        ret['data'] = data
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response

@app.route('/api/searchByLiteral/<doc_name>', methods=['POST'])
def search_by_literal(doc_name):
    query = request.json.get('query')
    search_apis = SEARCH_services[doc_name].search_literally(query.lower())
    data = []
    ret = {
        'success': True,
        'data': []
    }
    try:
        for api, score in search_apis:
            id, desc = HOMURA_services[doc_name].get_api_id_short_description(api)
            data.append({
                'name': get_api_qualified_name_from_entity_id(api),
                'description': desc,
                'id': id
            })
        ret['data'] = data
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/searchByConcept/<doc_name>', methods=['POST'])
def search_by_concept(doc_name):
    query = request.json.get('query')
    search_apis = SEARCH_services[doc_name].search_by_concept(query.lower())
    data = []
    ret = {
        'success': True,
        'data': []
    }
    try:
        for api, score in search_apis:
            id, desc = HOMURA_services[doc_name].get_api_id_short_description(
                api)
            data.append({
                'name': get_api_qualified_name_from_entity_id(api),
                'description': desc,
                'id': id
            })
        ret['data'] = data
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


@app.route('/api/search/<doc_name>', methods=['POST'])
def search_synthesis(doc_name):
    query = request.json.get('query')
    search_apis = SEARCH_services[doc_name].search_synthesis(query.lower())
    data = []
    ret = {
        'success': True,
        'data': []
    }
    try:
        for api, score in search_apis:
            id, desc = HOMURA_services[doc_name].get_api_id_short_description(
                api)
            data.append({
                'name': get_api_qualified_name_from_entity_id(api),
                'description': desc,
                'id': id,
                'score': score
            })
        ret['data'] = data
    except Exception as e:
        ret['success'] = False
        ret['reason'] = str(e)
    response = flask.make_response(jsonify(ret))
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
