import time
import sys
import json
import os

def composeSpaceResMsg(errormsg, msginfo, errorcode) :
    ret_msg = ''
    strmsg = ''
    space_res_msg = {}
    for key,value in errormsg.items() :
        tmpstrmsg = key + ': ' + msginfo + '. '
        strmsg += tmpstrmsg
    space_res_msg['code'] = errorcode
    space_res_msg['message'] = strmsg
    ret_msg = json.dumps(space_res_msg)
    return ret_msg

def composeSpaceResMsg_taskResult(errormsg, msginfo, errorcode) :
    ret_msg = ''
    strmsg = ''
    space_res_msg = {}

    if(errorcode == 10503): 
        return '{"code":10503, "message": "no execution result returned"}'

    for key,value in errormsg.items() :
        tmpstrmsg = key + ': ' + msginfo + '. '
        strmsg += tmpstrmsg
    space_res_msg['code'] = errorcode
    space_res_msg['message'] = strmsg
    ret_msg = json.dumps(space_res_msg)
    return ret_msg

def getRequestParamErrorResult(path, errormsg):
    print("request param result enter")

    ret_msg = ''
    if path == '/api/v2/taskboard/task/page' :
        ret_msg = composeSpaceResMsg(errormsg, 'Not a valid number', 400)
    elif path == '/api/v2/taskboard/task/delete' :
        ret_msg = composeSpaceResMsg(errormsg, 'Not a valid number', 400)
    elif path == '/api/v2/taskboard/getTaskResult' :
        if 'kpi' in errormsg :
            ret_msg = composeSpaceResMsg_taskResult(errormsg, '', 10503)
        else :
            ret_msg = composeSpaceResMsg(errormsg, 'no execution result returned', 404)

    else :
        ret_msg = 'not_space_res'
    
    return ret_msg

def test_errorResult():
    
    '''
    path = '/api/v2/taskboard/task/page'
    errormsg = {}
    errormsg['pageNum'] = '12312'
    errormsg['pageSize'] = '23244'
    '''

    '''
    path = '/api/v2/taskboard/task/page'
    errormsg = {}
    errormsg['taskid'] = '12312'
    '''
    path = '/api/v2/taskboard/getTaskResult'
    errormsg = {}
    errormsg['taskid'] = '12312'
    errormsg['abc'] = '12312'
    errorResult = getRequestParamErrorResult(path, errormsg)
    if errorResult != 'not_space_res':
        return errorResult, 200
    else :
        return 'request error_eee: %s' % ''.join(
            [('%s: %s; ' % (x, ''.join(y))) for x, y in errormsg.items()]), 400

if __name__ == "__main__":
    print('begin test')
    ret = test_errorResult()
    print('response is : ', ret)
    sys.exit(0)