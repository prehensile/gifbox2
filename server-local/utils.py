import os
import json 
import logging
import logging.handlers
import sys


def load_json( path, default_content=None ):
    j = None
    if os.path.exists( path ):
        with open( path ) as fp:
            j = json.load( fp )
    elif default_content is not None:
        dump_json( path, default_content )
        return default_content
    return j


def set_json( path, key, value ):
    j = load_json( path )
    j[ key ] = value
    with open( path, "w" ) as fp:
        fp.write( json.dumps(j) )
    return j


def dump_json( path, j ):
    with open( path, "w" ) as fp:
        fp.write( json.dumps(j) )
    return j


def init_logging( log_level=logging.DEBUG, debug_mode=False ):

    logger = logging.getLogger()
    logger.setLevel( log_level )

    handler = None
    if debug_mode:
        handler = logging.StreamHandler( sys.stdout )
    else:
        log_address = '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log'
        formatter = logging.Formatter('gifbox: %(message)s')
        handler = logging.handlers.SysLogHandler( address=log_address )
        handler.setFormatter( formatter )
    
    logger.addHandler( handler )
    