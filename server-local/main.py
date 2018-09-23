import os, sys
import random
import logging
import json

from flask import Flask, jsonify, send_from_directory, url_for

from flask_cors import CORS


app = Flask(
    __name__,
    static_folder="static"
)

CORS( app, resources={r"/api/*": {"origins": "*"}} )

logging.getLogger('flask_cors').level = logging.DEBUG


def media_dir():
    media_path = os.environ.get( 'GIFBOX_MEDIA' )
    media_path = os.path.realpath( media_path )
    print( media_path )
    return media_path


@app.route('/api/config')
def config():
    config = None
    with open( "config/config.json" ) as fp:
        config = fp.read()
    config = json.loads( config )
    return jsonify( config )


@app.route('/api/media/next')
def index():
    all_files = os.listdir( media_dir() )
    next_file = random.choice( all_files )
    url = url_for(
        'get_media',
        media_file=next_file,
        _external=True
    )
    return jsonify({
        "mediaItem" : {
            "src" : next_file,
            "url" : url
        } 
    })


@app.route('/media/<media_file>')
def get_media( media_file ):
    return send_from_directory(
        media_dir(),
        media_file
    )
    