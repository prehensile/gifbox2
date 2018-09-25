import os
import sys
import random
import logging
import atexit
import datetime

from flask import Flask, jsonify, send_from_directory, url_for, redirect, session, render_template, request, Response

from flask_cors import CORS

import utils
import dropboxclient


# init flask app
app = Flask(
    __name__,
    static_folder="static"
)

# init CORS
CORS( app, resources={r"/api/*": {"origins": "*"}} )
logging.getLogger('flask_cors').level = logging.DEBUG

# init logging
utils.init_logging(
    debug_mode = app.debug
)

# init flask session key
_PTH_FLASK_CONFIG = "config/flask.json"
_KEY_SESSION = "secret_key"
def get_session_key():
    sc = None
    flask_config = utils.load_json( _PTH_FLASK_CONFIG, default_content={} )
    if _KEY_SESSION not in flask_config:
        sc = "%r" % os.urandom(16)
        utils.set_json(
            _PTH_FLASK_CONFIG,
            _KEY_SESSION,
            sc
        )
    else:
        sc = flask_config[ _KEY_SESSION ]
    return sc

app.secret_key = get_session_key()


## 
# webapp config helpers
#

_CONFIG = None
_PTH_CONFIG = "config/config.json"
_CONFIG_KEY_DROPBOX_CONFIGURED = 'dropboxConfigured'

def get_config( key=None ):
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = utils.load_json( _PTH_CONFIG, default_content={} )
    if key:
        return _CONFIG[ key ]
    return _CONFIG


def set_config( key, value ):
    global _CONFIG
    _CONFIG = utils.set_json(
        _PTH_CONFIG,
        key,
        value
    )


## 
# route helpers
#

def media_dir():
    media_path = os.environ.get( 'GIFBOX_MEDIA' )
    media_path = os.path.realpath( media_path )
    return media_path


##
# dropbox client
#

_DB_CLIENT = None
_PTH_DB_CLIENT_CONFIG = "config/dropbox_client.json"
_DB_KEY_ACCESS_TOKEN = "access_token"

def init_dropbox():
    global _DB_CLIENT
    j = utils.load_json( _PTH_DB_CLIENT_CONFIG, default_content={} )
    token = j[ _DB_KEY_ACCESS_TOKEN ]
    _DB_CLIENT = dropboxclient.DropboxClient(
        access_token = token,
        media_path_local = media_dir(),
        media_path_remote="/gifplayer/media",
    )
    _DB_CLIENT.run()

if get_config( _CONFIG_KEY_DROPBOX_CONFIGURED ):
    init_dropbox()
    atexit.register( _DB_CLIENT.stop )


## 
# API routes
#

@app.route('/api/config')
def config():
    return jsonify(
        get_config()
    )


@app.route('/api/media/next')
def next_media():

    next_file = None

    if 'since' in request.args:
        since = datetime.datetime.fromisoformat(
            request.args[ 'since' ]
        )
        new_files = _DB_CLIENT.files_since( since )
        if len( new_files ) > 0:
            next_file = new_files[0]

    if next_file is None:
        all_files = os.listdir( media_dir() )
        next_file = random.choice( all_files )
    
    url = url_for(
        'get_media',
        media_file=next_file,
        _external=True
    )
    
    now = datetime.datetime.now()
    return jsonify({
        "mediaItem" : {
            "src" : next_file,
            "url" : url
        },
        "timestamp" : now.isoformat() 
    })


## 
# media routes
#

@app.route('/media/<media_file>')
def get_media( media_file ):
    return send_from_directory(
        media_dir(),
        media_file
    )


##
# ADMIN ROUTES
#

@app.route('/admin')
def admin():
    
    c = get_config()

    url_dropbox_auth = None
    if not c[ "dropboxConfigured" ]:
        url_dropbox_auth = url_for(
            'dropbox_auth_start'
        )

    return render_template(
        'admin.html',
        url_dropbox_auth = url_dropbox_auth,
        config = c
    )



##
# DROPBOX AUTH ROUTES
#

from dropbox import DropboxOAuth2Flow
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException

_PTH_DB_SECRET_CONFIG = "config/dropbox_secret.json"

def get_dropbox_auth_flow():
    redirect_uri = url_for(
        'dropbox_auth_finish',
        _external=True
    )
    
    j = utils.load_json( _PTH_DB_SECRET_CONFIG )
    
    return DropboxOAuth2Flow(
        j["APP_KEY"],
        j["APP_SECRET"],
        redirect_uri,
        session,
        "dropbox-auth-csrf-token"
    )


# URL handler for /dropbox-auth-start
@app.route('/auth/start')
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow().start()
    return redirect( authorize_url )


def handle_exception( e, status_code ):
    return Response(
        "%r" % e ,
        status=status_code,
        mimetype='application/json'
    )


# URL handler for /dropbox-auth-finish
@app.route('/auth/finish')
def dropbox_auth_finish():
    
    try:
        oauth_result = get_dropbox_auth_flow().finish(request.args)
        utils.dump_json(
            "config/dropbox_client.json",
            {
                _DB_KEY_ACCESS_TOKEN : oauth_result.access_token,
                "account_id" : oauth_result.account_id,
                "user_id" : oauth_result.user_id,
            }
        )
        set_config( "dropboxConfigured", True )
        init_dropbox()
        return redirect( "admin" )
    
    except BadRequestException as e:
        return handle_exception( e, 400 )
    
    except BadStateException as e:
        # Start the auth flow again.
        return redirect( "dropbox_auth_start" )
    
    except CsrfException as e:
        return handle_exception( e, 403 )
    
    except NotApprovedException as e:
        # Not approved?  Why not? 
        return redirect( "admin" )
    
    except ProviderException as e:
        #logger.log("Auth error: %s" % (e,))
        print( "Auth error: %s" % (e,) )
        return handle_exception( e, 403 )
    
