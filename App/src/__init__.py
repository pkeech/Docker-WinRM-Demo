## IMPORT MODULES 
from flask import Flask, request, jsonify
import os, logging

## IMPORT BLUEPRINTS
from src.blueprints.page import page

## DEFINE FLASK APPLICATION
def create_app(settings_override=None):

    ## DEFINE LOGGING STANDARDS
    logging.basicConfig(level=logging.DEBUG,
        format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler()])

    logger = logging.getLogger()

    ## INITIALIZE FLASK AND EXTENSIONS
    app = Flask(__name__)

    ## LOG APPLICATION START UP
    logger.info('Starting Application ...')

    ## Load Flask App Configurations
    #app.config.from_object('src.config')

    ## Import Views (After App Initialzed)
    app.register_blueprint(page)

    ## LOG APPLICATION START UP
    logger.info('Application Started')

    ## RETURN APPLICATION
    return app