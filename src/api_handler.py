
import json
import traceback
from handler import lambda_handler as handler

ALLOWED_RESOURCES = [
    'github_auth',
    'google_auth',
    'sso_auth',
    'group',
    'user',
    'invited_user',
    'order'
]

def lambda_handler(event, context):

    print 'Received event:\n%s' % event

    method = event['httpMethod'].lower()
    paths = event['path'].split('/')
    path = paths[len(paths)-1]
    res_type = event.get('resType')
    print 'method: %s' % method
    print 'paths: %s' % paths
    print 'path: %s' % path
    print 'res_type: %s' % res_type

    resource = path
    if resource not in ALLOWED_RESOURCES:
        print "not supported resource, %s" % resource
        raise Exception("not found")

    query_params = event.get('queryStringParameters')
    if not query_params:
        query_params = {}
    elif isinstance(query_params, str) or isinstance(query_params, unicode):
        query_params = json.loads(query_params)
    post_data = event.get('body')
    if not post_data:
        post_data = {}
    elif isinstance(post_data, str) or isinstance(post_data, unicode):
        post_data = json.loads(post_data)
    params = post_data;
    if method == 'get':
        params = query_params;
    print 'resource: %s' % resource
    print 'parameters: %s' % params

    oper = params.get('oper')
    print 'oper: %s' % oper
    if oper is None:
        if method == 'get':
            if params and params.get('id'):
                oper = 'find_by_id'
            else:
                oper = 'find'
        elif method == 'post':
            oper = 'create'
        elif method == 'put':
            oper = 'update'
        elif method == 'delete':
            oper = 'delete'
    else:
        del params['oper']
    print 'converted oper: %s' % oper

    access_token = event['headers'].get('Authorization')
    print 'access_token: %s' % access_token

    handler_event = {'access_token': access_token, 'resource': resource, 'oper': oper, 'params': json.dumps(params)}

    try:
        ret = handler(handler_event, context)
        response = { 'statusCode': 200 };
        if res_type and res_type == 'json':
            response['body'] = ret
        else:
            response['headers'] = { "Access-Control-Allow-Origin": "*" }
            response['body'] = json.dumps(ret)
        return response
    except Exception, ex:
        traceback.print_exc()
        err_msg = '%s' % ex
        if err_msg == 'not permitted':
            status_code = 401
        elif err_msg == 'unauthorized':
            status_code = 403
        elif err_msg == 'not found':
            status_code = 404
        else:
            status_code = 500
        response = { 'statusCode': status_code };
        if res_type and res_type == 'json':
            response['body'] = err_msg
        else:
            response['headers'] = { "Access-Control-Allow-Origin": "*" }
            response['body'] = json.dumps(err_msg)
        return response
