## IMPORT REQUIRED PYTHON MODULES
import winrm, json, urllib3, os, base64

## IMPORT REQUIRED FLASK MODULES
from flask import Blueprint, request, jsonify, make_response, current_app, render_template, send_file

## DEFINE BLUEPRINTS
page = Blueprint('page', __name__, template_folder='templates')

## DISABLE URLLIB WARNINGS (THIS DOESN'T WORK WITH PYWINRM)
#urllib3.disable_warnings()

## FUNCTION: EXTRACT JSON FROM STRING
def ExtractJSON(rawText):
    ## HANDLE JSON WITH/WITHOUT ARRAY
    if rawText.find('[') != -1:
        firstValue = rawText.index("[")
        lastValue = len(rawText) - rawText[::-1].index("]")
    elif STDOUT.find('{') != -1:
        firstValue = rawText.index("{")
        lastValue = len(rawText) - rawText[::-1].index("}")
    else:
        ## RETURN NOTHING
        return None

    ## EXTRACT JSON
    RESULTS = rawText[firstValue:lastValue]

    ## RETURN JSON OBJECT
    return RESULTS

## FUNCTION: EXTRACT OUTPUT FROM STRING
def ExtractOutput(rawText):
    ## HANDLE JSON WITH/WITHOUT ARRAY
    if rawText.find('[') != -1:
        firstValue = rawText.index("[")
        lastValue = len(rawText) - rawText[::-1].index("]")
    elif STDOUT.find('{') != -1:
        firstValue = rawText.index("{")
        lastValue = len(rawText) - rawText[::-1].index("}")
    else:
        ## RETURN NOTHING
        return None

    ## EXTRACT JSON
    RESULTS = rawText[firstValue:lastValue]
    RESULTS = rawText.replace(RESULTS, '')

    ## RETURN RESULTS
    return RESULTS

## ROUTE: HOME
@page.route("/")
def index():
    ## RETURN HELLO WORLD
    return render_template('index.html')

## ROUTE: FILE
@page.route("/file")
def pageFile():
    return render_template('file.html')

## DOWNLOAD: DOWNLOAD SAMPLE JSON FILE
@page.route("/download")
def download():
    ## CREATE PATH
    #uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    path = os.path.join(current_app.root_path, "/app/src/files/sample_assets.json")
    
    ## DOWNLOAD FILE
    return send_file(path, as_attachment=True)

## PYTHON DECODE JAVASCRIPT BASE64
# base64.b64decode(JAVASCRIPT_ENCODED).decode('utf-8')
# base64.b64decode('Zm9ybS11cGxvYWRzLzIwMTUgUGVycnkncyBBd+RyZHMgTGV0dGVyLmpwZw==').decode('latin1')

## DEMO COMMAND
# $TEMP = '$$JSON$$'; $TEMP = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($TEMP)); $TEMP | Out-File -FilePath C:\Users\Administrator\Desktop\Test.json

## AJAX: EXECUTE POWERSHELL ROUTE
@page.route("/api/v1/powershell", methods=['POST'])
def powershell():
    ## READ JSON DATA
    req_data = request.get_json()

    ## PARSE PARAMETERS
    SERVER = req_data['server']
    USER = req_data['username']
    PASS = req_data['password']
    CMD = req_data['cmd']

    ## IF FILE IS PASSED UPDATE CMD
    if 'file' in req_data:
        ##LOAD FILE IF PASSED
        ENCODED_FILE = req_data['file']
   
        ## SEARCH FOR REPLACEMENT
        if '$$JSON$$' in CMD:
            CMD = CMD.replace('$$JSON$$', ENCODED_FILE )

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

        ## CONVERT STDOUT TO STRING
        STDOUT = r.std_out.decode('utf-8')
        STDERR = r.std_err.decode('utf-8')

        ## ATTEMPT TO FIND JSON WITHIN STDOUT
        try:
            ## EXTRACT JSON FROM TEXT
            RawJSON = ExtractJSON(STDOUT)

            ## EXTRACT OUTPUT FROM TEXT
            RawOutput = ExtractOutput(STDOUT)

            try:
                ## CONVERT STRING TO JSON
                RESULTS = json.loads(RawJSON)

                ## CREATE RESPONSE
                resp = make_response(jsonify({
                    'status': "Success",
                    'response': RawOutput,
                    'json': RESULTS,
                    'errors': STDERR
                }), 200)
            except ValueError as e:
                ## CREATE ERROR RESPONSE
                resp = make_response(jsonify({
                    'status': "Failed",
                    'response': f'Powershell Script Returned an Invalid Response. Error Message: { e }',
                    'json': '',
                    'errors': f'Powershell Script Returned an Invalid Response. Error Message: { e }'
                }), 200)

        except:
            resp = make_response(jsonify({
                'status': "Succss",
                'response': f'{ STDOUT }',
                'json': '',
                'errors': f'{ STDERR }'
            }), 200)
    else:
        ## CREATE RESPONSE
        resp = make_response(jsonify({
            'status': "Failed",
            'response': f'Powershell Script Return a Failed Code. Error Message: { r.std_err }',
            'json': '',
            'ps_status_code': r.status_code,
            'errors': f'Powershell Script Return a Failed Code. Error Message: { r.std_err }'
        }), 200)

    ## RETURN RESPONSE
    return resp

## FUNCTION: RUN POWERSHELL COMMANDS
def runPowershell(SERVER, USER, PASS, CMD):
    ## ATTEMPT TO RUN POWERSHELL COMMAND ON REMOTE SYSTEM
    try:
        ## DEFINE CONNECTION & RUN COMMAND
        s = winrm.Session(SERVER, auth=(USER, PASS), transport='ntlm')
        r = s.run_ps(CMD)
        
        ## RETURN RESULTS
        return r
    except Exception as e:
        ## RETURN ERROR MESSAGE
        print(f"[ERROR] Message: { str(e) }", flush=True)
        return str(e)

## AJAX: EXECUTE POWERSHELL ROUTE
@page.route("/api/v1/powershell/upload", methods=['POST'])
def powershellUpload():
    ## READ JSON DATA
    req_data = request.get_json()
    
    ## PARSE JSON
    SERVER = req_data['server']
    USER = req_data['username']
    PASS = req_data['password']
    PATH = req_data['path']
    ENCODED_FILE_DATA = req_data['file']

    ## LOG: VERIFY DIRECTORY
    LOGS = "[INFO] Testing File Directory Exists ... \n"

    ## SPLIT FILEPATH
    SPLIT_PATH = PATH.rsplit("\\", 1)
    
    ## RUN POWERSHELL COMMAND
    RESULTS = runPowershell(SERVER, USER, PASS, f"Test-Path { SPLIT_PATH[0] }")

    ## ERROR HANDLE
    if RESULTS.status_code != 0:
        ## LOG: LOG ERROR MESSAGE
        LOGS += "[FAILED] Unable to connect or run Powershell command on remote host."
        
        ## GENERATE RESPONSE AND RETURN
        resp = make_response(jsonify({
            'status': "Failed",
            'logs': LOGS,
            'message': RESULTS.std_err,
            'status_code': RESULTS.status_code
        }), 503)

        return resp

    ## FORMAT RESPONSE
    POWERSHELL_RESULT = (RESULTS.std_out.decode('utf-8')).replace('\r\n', '')

    ## ENSURE DIRECTORY EXISTS
    if POWERSHELL_RESULT != "True":
        ## LOG: LOG ERROR MESSAGE
        LOGS += "[FAILED] Either the specified directory doesn't exist or the account doesn't have permissions."
        
        ## GENERATE RESPONSE AND RETURN
        resp = make_response(jsonify({
            'status': "Failed",
            'logs': LOGS,
            'message': "Either the specified directory doesn't exist or the account doesn't have permissions.",
            'status_code': RESULTS.status_code
        }), 200)

        return resp

    ## LOG: VERIFY DIRECTORY
    LOGS += "[INFO] File Directory Exists !!!\n"

    ## LOG: ATTEMPT TO CREATE FILE
    LOGS += "[INFO] Attempting to Transfer file to remote system ...\n"

    ## CREATE FILE ON REMOTE SERVER
    CMD = f"$TEMP = '{ ENCODED_FILE_DATA }'; $TEMP = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($TEMP)); $TEMP | Out-File -FilePath { PATH }"
    RESULTS = runPowershell(SERVER, USER, PASS, CMD)

    ## ERROR HANDLE
    if RESULTS.status_code != 0:
        ## LOG: LOG ERROR MESSAGE
        LOGS += "[FAILED] Unable to create file on remote host."
        
        ## GENERATE RESPONSE AND RETURN
        resp = make_response(jsonify({
            'status': "Failed",
            'logs': LOGS,
            'message': RESULTS.std_err,
            'status_code': RESULTS.status_code
        }), 503)

        return resp

    ## LOG: VERIFY DIRECTORY
    LOGS += "[SUCCESS] File Transfered Successfully!"

    ## FAKE RESPONSE
    resp = make_response(jsonify({
        'status': "Success",
        'logs': LOGS
    }), 200)

    ## RETURN RESPONSE
    return resp