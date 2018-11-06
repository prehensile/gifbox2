

class GifBox {
  

  constructor(){
    this._clock = null;
    this._config = null;
    this._wsClient = null;
    this._selfAdvance = null;  // if true, will advance from gif to gif automatically
  }


  _loadJson( url, callback, params ){
    let request = new XMLHttpRequest();  
    
    if( params ){
      let pairs = [];
      for (const key in params) {
        if (params.hasOwnProperty(key)) {
          pairs.push(
            key + "=" + encodeURIComponent( params[key] )
          );
        }
      }
      url = url + "?" + pairs.join("&");
    }  

    request.responseType = 'json';

    request.open( 'GET', url, true );

    request.onreadystatechange = function (oEvent) {  
      if (request.readyState === 4) {  
        if (request.status === 200) {  
          callback( request.response );
        } else {  
          console.log( "Error", request.statusText );  
        }  
      }  
    };  

    request.send();  

    return request;
  }


  loadNextImageAfterTimeout( timeout ){
    let thisRef = this;
    this._advanceTimeout = setTimeout( function(){
        thisRef.loadNextImageData();
        thisRef._advanceTimeout = null;
    }, timeout );
  }

  setSelfAdvance( selfAdvance ){
    
    console.log( "setSelfAdvance", selfAdvance );

    // don't do anything if we don't need to
    if( selfAdvance == this._selfAdvance ) return;

    this._selfAdvance = selfAdvance;

    if( selfAdvance ){
      this.loadNextImageData();
    } else {  
      if( this._advanceTimeout ) {
        clearTimeout( this._advanceTimeout );
      }
    }

  }

  prepareLoadedImage(){

    let lastImg = document.getElementById( 'imgLast' );
    
    let nextImg = document.getElementById( 'imgLoading' );
    this.fitImageToContainer( nextImg );

    lastImg.parentNode.removeChild( lastImg );
    nextImg.classList.remove( 'hidden' );

    nextImg.id = 'imgLast';

  } 


  fitImageToContainer( image ){
    
    let pn = image.parentNode;
    let imgAspectRatio = image.naturalHeight / image.naturalWidth;
    let parAspectRatio = pn.offsetHeight / pn.offsetWidth;

    if( parAspectRatio > imgAspectRatio ){
      image.classList.remove( 'fitWidth' );
      image.classList.add( 'fitHeight' );
    }
  }


  onNextImageLoaded(){
    this.prepareLoadedImage();

    if( this._selfAdvance ) {
      this.loadNextImageAfterTimeout( 8000 );
    }

    if( this._imageLoadedCallback ){
      this._imageLoadedCallback();
      this._imageLoadedCallback = null;
    }
  }


  spawnNextImage( src ){

    let nextImg = document.createElement('img');
    nextImg.id = "imgLoading";
    nextImg.src = src;
    nextImg.classList.add( 'fitWidth' );
    nextImg.classList.add( 'hidden' );  // hide until loaded

    let div = document.getElementById( "images" );
    div.appendChild( nextImg );

    return nextImg;
  }


  onNextImageData( imageData ){
    
    this._lastImageData = imageData;

    let nextImg = this.spawnNextImage(
        imageData.mediaItem.url
    );
    
    let thisRef = this;

    nextImg.onload = function(){
        thisRef.onNextImageLoaded();
    }

  }


  loadNextImageData(){

    let thisRef = this;
    
    let params = null;
    if( this._lastImageData ){
      params = {
        "since" : this._lastImageData[ "timestamp" ]
      }
    }

    this._loadJson(
      '/api/media/next',
      function( data ){
        thisRef.onNextImageData( data );
      },
      params
    )
      
  }


  loadConfig( callback ){
    let thisRef = this;
    this._loadJson(
      '/api/config',
      callback
    )
  }
  

  applyConfig( config ){
    
    console.log( config );
    debugger;

    this._config = config;

    const thisRef = this;

    // set up clock
    if( config.showClock ){
    //if( true ){
      
      // clock should be on
      if( !this._clock ){
        this._clock = new Clock( "images/clock/digit-" );
      }

      // stop refreshing gifs with our own timer
      this.setSelfAdvance( false );

      // use displayed clock time change to refresh gifs
      this._clock.onClockChange = function(){
        thisRef.loadNextImageData();
      }

      this._clock.run();
      this._clock.show();
    
    } else {
     
      // clock should be off
      if( this._clock ){
        
        // remove callback to refresh gif on displayed time change
        this._clock.onClockChange = null;
        
        this._clock.stop();
        this._clock.hide();
      }

      // start refreshing gifs with our own timer
      this.setSelfAdvance( true );
    }

  }


  postIntro(){
    // debugger;
    const thisRef = this;

    // load config, then do the next thing
    this.loadConfig( function(data){
      thisRef.applyConfig( data );
    });
  }


  connectSockets(){

    this._wsClient = new WebSocketClient();
    
    const thisRef = this;
    this._wsClient.onConfigReceived = function( config ){
      thisRef.applyConfig( config );
    }    

    this._wsClient.connect( "localhost:5000" );  
  }


  init(){
    
    // bootstrap gifbox

    // fit default image to screen
    let img = document.getElementById("imgLast");
    this.fitImageToContainer( img );

    const thisRef = this;
    window.setTimeout( function(){
      thisRef.postIntro();
    },8000);
    
    this.connectSockets();
  }

}


window.onload = function() {
    
    const gifbox = new GifBox();
    gifbox.init();

    window.gifbox = gifbox;
}