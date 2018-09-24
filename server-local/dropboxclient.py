import os
import datetime
import logging
import threading
import time

import dropbox


class DropboxClient( object ):


    def __init__( self, access_token=None, media_path_local=None, media_path_remote=None  ):
        
        self._dbx = dropbox.Dropbox( access_token )
        self._media_path_remote = media_path_remote
        self._media_path_local = media_path_local

        # threading stuff...
        self._run_flag = None
        self._thread = None


    def _local_path_for_metadata( self, file_metadata ):
        """
        Returns a local path (in media folder) for a remote Dropbox file
        """
        return os.path.join(
            self._media_path_local,
            file_metadata.name
        )


    def download_file( self, file_metadata ):
        """
        Download the Dropbox file specified by file_metadata
        Local path is inferred using _local_path_for_metadata().
        """
        # TODO: queue this
        local_path = self._local_path_for_metadata( file_metadata )
        print( "Will download {} to {}".format( file_metadata.path_lower, local_path ) )
        self._dbx.files_download_to_file(
            local_path,
            file_metadata.id
        )


    def sync_from_server( self ):
        """
        Perform a single sync from Dropbox to local media folder.
        Downloads all files that don't exist locally, or are newer than local equivalents.
        """

        # TODO: remove deleted files

        # list all remote files
        resp = self._dbx.files_list_folder( self._media_path_remote )
        
        # step through remote files
        for file_metadata in resp.entries:
            
            # by default, download files
            should_download_file = True
            
            # get possible local path for remote file
            local_path = self._local_path_for_metadata( file_metadata )
            
            # if this path already exists locally...
            if os.path.exists( local_path ):

                # get last modification date for local file
                s = os.stat( local_path )
                dt_local = datetime.datetime.fromtimestamp( s.st_mtime )

                # if remote file is older, or the same age as local file...
                if file_metadata.server_modified <= dt_local:
                    # ..don't download it
                    should_download_file = False

            if should_download_file:
                self.download_file( file_metadata )
        
        # return cursor from initial listing so we could e.g. use it for getting updates
        return resp.cursor


    def files_since( self, dt ):
        """
        Returns a list of all locally downloaded files which have been modified
        since the timestamp specified in dt (a datetime.datetime object).
        """
        new_files = []
        
        # sort local media files by modify date, descending
        listed = sorted(
            os.scandir( self._media_path_local ),
            key=lambda item: item.stat().st_mtime,
            reverse = True
        )
        
        # get timestamp from passed datetime object
        ts = dt.timestamp()
        
        # step through sorted files, bail as soon as we reach one older than ts
        for item in listed:
            if item.stat().st_mtime <= ts:
                break
            new_files.append( item.name  )
        
        return new_files
    

    # this should probably run on a thread?
    def update_forever( self, flag ):
        logging.debug( "DropboxClient.update_forever()" )
        # do initial update, get cursor
        cursor = self.sync_from_server()
        while not flag.is_set():
            
            logging.debug( "DropboxClient start long poll..." )
            
            longpoll_res = self._dbx.files_list_folder_longpoll( cursor, timeout=30 )
            
            logging.debug( "... result is: %r", longpoll_res )
            
            # if longpoll reports any changes...
            if longpoll_res.changes:
                
                # TODO: deal with deletions

                # list changed files
                list_res = self._dbx.files_list_folder_continue( cursor )
                
                # download changed files
                for file_metadata in list_res.entries:
                    self.download_file( file_metadata )
                
                # set cursor
                cursor = list_res.cursor
            
            # backoff if asked to
            if longpoll_res.backoff:
                time.sleep( longpoll_res.backoff )
            
            logging.debug( "... DropboxClient long poll ended, start another" )
        
        logging.debug( "... DropboxClient.update_forever() finished" )
    

    def run( self ):
        logging.debug( "DropboxClient.run()" )
        self._run_flag = threading.Event()
        self._thread = threading.Thread(
            name='DropboxDaemon',
            target=self.update_forever,
            daemon=True,
            args=[self._run_flag]
        )
        self._thread.start()
    

    def stop( self ):
        logging.debug( "DropboxClient.stop()" )
        if self._run_flag and self._thread:
            self._run_flag.set()
            self._thread.join()


def main():
    dbc = DropboxClient(
        access_token=os.getenv( 'DROPBOX_TOKEN' ),
        media_path_remote="/gifplayer/media",
        media_path_local=os.getenv( 'GIFBOX_MEDIA' )
    )
    dbc.sync_from_server()

    dt = datetime.datetime.fromtimestamp(1537388308)
    print(
        dbc.files_since( dt )
    )

if __name__ == '__main__':
    main()