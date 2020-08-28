## IMPORT REQUIRED PYTHON MODULES
import winrm, json, urllib3

## IMPORT REQUIRED FLASK MODULES
from flask import request, jsonify, make_response, current_app, render_template

## IMPORT REQUIRED CUSTOM MODULES
from src import app

## DISABLE URLLIB WARNINGS
urllib3.disable_warnings()

## HOME ROUTE
@app.route("/")
def index():
    ## RETURN HELLO WORLD
    return render_template('index.html')

## EXECUTE POWERSHELL ROUTE
@app.route("/api/v1/powershell", methods=['POST'])
def powershell():
    ## READ JSON DATA
    req_data = request.get_json()

    ## PARSE PARAMETERS
    SERVER = req_data['server']
    USER = req_data['username']
    PASS = req_data['password']
    CMD = req_data['cmd']
   
    try:
        ## CREATE CONNECTION STRING
        s = winrm.Session(SERVER, auth=(USER, PASS), transport='ntlm')
        
        ## ATTEMPT TO EXECUTE PWSH COMMAND
        r = s.run_ps(CMD)
    except Exception as e:
        resp = make_response(jsonify({
            'status': "Failed",
            'message': str(e)
        }), 503)

    ## VERIFY SCRIPT SUCCESS
    if r.status_code == 0:
        ## CONVERT RESULTS
        jRESULTS = json.loads(r.std_out)

        ## CREATE RESPONSE
        resp = make_response(jsonify({
                'status': "Success",
                'results': jRESULTS
            }), 200)
    else:
        ## CREATE RESPONSE
        resp = make_response(jsonify({
            'status': "Failed",
            'results': 'Powershell Script Return a Failed Code',
            'ps_status_code': r.status_code
        }), 200)

    ## RETURN RESPONSE
    return resp