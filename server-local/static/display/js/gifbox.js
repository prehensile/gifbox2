

class GifBox {
  

  constructor(){
    this._clock = null;
    this._config = null;
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


  loadNextImage(){
    let thisRef = this;
    setTimeout( function(){
        thisRef.loadNextImageData();
    }, 8000 );
  }


  prepareLoadedImage(){

    let lastImg = document.getElementById( 'imgLast' );
    
    let nextImg = document.getElementById( 'imgLoading' );
    this.fitImageToContainer( nextImg );

    lastImg.parentNode.removeChild( lastImg );
    nextImg.classList.remove( 'loading' );

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
    //this.loadNextImage();
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
    nextImg.classList.add( 'loading' );

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
      function( data ){
        thisRef.onConfigLoaded( data, callback )
      }
    )
  }
  

  onConfigLoaded( data, callback ) {
    this._config = data;
    if( callback ){
      callback();
    }
  }


  initClock() {
    if( this._config.showClock ){
      if( !this._clock ){
        const c = new Clock( "images/clock/digit-" );
        c.run();
        this._clock = c;
      }
    }  
  }

  postIntro(){
    
    const thisRef = this;

    // load config, then do the next thing
    this.loadConfig( function(){
      debugger;
      thisRef.initClock();
      thisRef._clock.onClockChange = function(){
        console.log( "onClockChange" );
        thisRef.loadNextImageData();
      };
      thisRef.loadNextImageData();
    });
  }

  init(){
    
    // bootstrap gifbox

    let img = document.getElementById("imgLast");
    this.fitImageToContainer( img );

    const thisRef = this;
    window.setTimeout( function(){
      thisRef.postIntro();
    },8000);
    
  }

}


window.onload = function() {
    
    const gifbox = new GifBox();
    gifbox.init();

}