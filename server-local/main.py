import os
import random
import logging
import atexit
import datetime
import json
from threading import Event

from flask import Flask, jsonify, send_from_directory, url_for, redirect, session, render_template, request, Response
from werkzeug.utils import secure_filename

from flask_cors import CORS
from flask_sockets import Sockets

import gevent

import utils
import dropboxclient


# init flask app
app = Flask(
    __name__,
    static_folder="static"
)

# init websockets
sockets = Sockets(app)

# init CORS
CORS( app, resources={r"/api/*": {"origins": "*"}} )
# logging.getLogger('flask_cors').level = logging.DEBUG

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
        sc = utils.random_string( 16 )
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
    
    # if config hasn't been read from disk yet...
    if _CONFIG is None:
        # ...read it
        _CONFIG = utils.load_json( 
            _PTH_CONFIG,
            # by default, dropbox isn't configured
            default_content={
                _CONFIG_KEY_DROPBOX_CONFIGURED : False
            }
        )
    
    # if we've been asked for the value of a specific key, return that
    if key:
        return _CONFIG[ key ]
    
    # otherwise, return whole config
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
    return os.path.realpath(
        os.environ.get( 'GIFBOX_MEDIA' )
    )


def upload_dir():
    return os.path.realpath(
        os.environ.get( 'UPLOAD_DIRECTORY' )
    )


##
# dropbox client
#

_DB_CLIENT = None
_PTH_DB_CLIENT_CONFIG = "config/dropbox_client.json"
_DB_KEY_ACCESS_TOKEN = "access_token"
_USE_DROPBOX = os.environ.get( "USE_DROPBOX", "yes" ) == "yes"

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

if get_config( _CONFIG_KEY_DROPBOX_CONFIGURED ) and _USE_DROPBOX:
    init_dropbox()
    atexit.register( _DB_CLIENT.stop )


##
# websockets
#

_CONFIG_CHANGED = Event()

@sockets.route('/sockets')
def socket( ws ):
    while not ws.closed:
        
        message = None
        with gevent.Timeout(0.5, False):
            message = ws.receive()
        
        if message is not None:
            logging.debug( "websocket message: %s", message )
        
        if _CONFIG_CHANGED.is_set():
            logging.debug( "!! SEND NEW CONFIG" )
            ws.send( json.dumps( get_config() ) )
            _CONFIG_CHANGED.clear()
    
    logging.debug("end of socket")

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
        if _DB_CLIENT:
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

@app.route('/overlay/<overlay_file>')
def get_overlay( overlay_file ):
    return send_from_directory(
        upload_dir(),
        overlay_file
    )


##
# ADMIN ROUTES
#

@app.route('/admin')
def admin():
    
    c = get_config()

    url_dropbox_auth = None
    url_dropbox_deauth = None
    if c[ _CONFIG_KEY_DROPBOX_CONFIGURED ]:
        url_dropbox_deauth = url_for(
            'dropbox_deauth'
        )
    else:
        url_dropbox_auth = url_for(
            'dropbox_auth_start'
        )

    overlay_checked = "rdoOverlayNone"
    if c['showClock']:
        overlay_checked = "rdoOverlayClock"
    elif c['overlay']:
        overlay_checked = "rdoOverlayPng"

    return render_template(
        'admin.html',
        url_dropbox_auth = url_dropbox_auth,
        url_dropbox_deauth = url_dropbox_deauth,
        overlay_checked = overlay_checked,
        config = c
    )


@app.route('/admin/dropbox/deauth')
def dropbox_deauth():
    
    # stop updating from dropbox
    _DB_CLIENT.stop()
    
    # write empty config
    utils.dump_json( _PTH_DB_CLIENT_CONFIG, {} )
    set_config( _CONFIG_KEY_DROPBOX_CONFIGURED, False )
    return redirect( "admin" )


def allowed_file( filename ):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'png'

@app.route('/admin/files/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file( file.filename ):
        filename = secure_filename( file.filename )
        file.save(
            os.path.join(
                upload_dir(),
                filename
            )
        )
        return redirect(
            url_for('admin')
        )


@app.route( '/api/admin/state', methods=['POST'] )
def admin_state():
    
    state = request.get_json()
    
    print( state )

    set_config(
        'showClock',
        state['rdoOverlay'] == 'clock' 
    )

    k_overlay = "fileOverlay"
    if (k_overlay in state) and ( len(state[k_overlay])>1 ):
        set_config(
            'overlay',
            state[k_overlay]
        )
    else:
        set_config(
            'overlay',
            None
        )


    # set this flag so that the websocket connection to the client will send the new config
    _CONFIG_CHANGED.set()

    return jsonify(
        state
    )


##
# DROPBOX AUTH ROUTES
#

from dropbox import DropboxOAuth2Flow
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException

_PTH_DB_SECRET_CONFIG = "config/dropbox_secret.json"
_PTH_DB_CLIENT_CONFIG = "config/dropbox_client.json"

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
            _PTH_DB_CLIENT_CONFIG,
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


##
# main
#

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    
    port = int( os.environ.get( "FLASK_RUN_PORT", "5000" ) )
    host = os.environ.get( "FLASK_RUN_HOST", "" )

    server = pywsgi.WSGIServer(
        (host, port),
        app,
        handler_class=WebSocketHandler
    )
    
    server.serve_forever()