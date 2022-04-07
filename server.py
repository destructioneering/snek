import os

from flask import Flask
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory, jsonify

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SRC_FOLDER = os.path.join(basedir, './src')
    STATIC_FOLDER = os.path.join(basedir, './static')
    TEMPLATE_FOLDER = os.path.join(basedir, '.')

bp = Blueprint('routes', __name__)
bp.template_folder = Config.TEMPLATE_FOLDER

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html', title='snek')

@bp.route('/<path>', methods=['GET'])
def src(path):
    return send_from_directory(Config.SRC_FOLDER, path)

@bp.route('/static/<path>')
def static(path):
    return send_from_directory(Config.STATIC_FOLDER, path)

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(bp)
    return app

if __name__ == "__main__":
    app = create_app(Config)
    app.run(debug=True)
