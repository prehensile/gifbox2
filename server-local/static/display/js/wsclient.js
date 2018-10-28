class WebSocketClient {
  

  constructor(){
    this._ws = null;
    this.onConfigReceived = null;
  }


  connect( host ){
    
    this._socketHost = host;

    this._ws = new WebSocket(
      "ws://" + host + "/sockets",
      // "config"
    );

    const thisRef = this;
    
    this._ws.onopen = function(e){
      ( "hello from client" );
    }

    this._ws.onmessage = function( e ){
      console.log( e );
      thisRef.onMessage( e.data );
    }

    this._ws.onclose = function(e){
      console.log( e );
      thisRef.onClose();
    }

  }

  onClose(){
    // stay connected
    this.connect( this._socketHost );
  }

  onMessage( data ){
    const msg = JSON.parse( data );
    if( this.onConfigReceived ){
        this.onConfigReceived( msg );
    }
  }

}
