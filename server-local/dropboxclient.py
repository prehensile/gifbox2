import os
import datetime
import logging

import dropbox


class DropboxClient( object ):


    def __init__( self, access_token=None, media_path_local=None, media_path_remote=None  ):
        self._dbx = dropbox.Dropbox( access_token )
        self._media_path_remote = media_path_remote
        self._media_path_local = media_path_local


    def _local_path_for_metadata( self, file_metadata ):
        return os.path.join(
            self._media_path_local,
            file_metadata.name
        )


    def download_file( self, file_metadata ):
        # TODO: queue this
        local_path = self._local_path_for_metadata( file_metadata )
        print( "Will download {} to {}".format( file_metadata.path_lower, local_path ) )
        self._dbx.files_download_to_file(
            local_path,
            file_metadata.id
        )


    def sync_from_server( self ):
        
        resp = self._dbx.files_list_folder( self._media_path_remote )
        
        for file_metadata in resp.entries:
            
            should_download_file = True
            
            local_path = self._local_path_for_metadata( file_metadata )
            
            if os.path.exists( local_path ):

                s = os.stat( local_path )
                dt_local = datetime.datetime.fromtimestamp( s.st_mtime )

                if file_metadata.server_modified <= dt_local:
                    should_download_file = False

            if should_download_file:
                self.download_file( file_metadata )


    def files_since( self, dt ):

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
    

    # TODO: this should probably run on a thread?
    def update( self, cursor ):
        while True:
            longpoll_res = self._dbx.files_list_folder_longpoll( cursor, timeout=30 )
            if longpoll_res.changes:
                list_res = self._dbx.files_list_folder_continue( cursor )
                for file_metadata in list_res.entries:
                    self.download_file( file_metadata )


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