

class GifBox {
  

  constructor(){
    this._clock = null;
    this._config = null;
  }


  _loadJson( url, callback ){
    let request = new XMLHttpRequest();  
    
    request.open(
        'GET',
        url,
        true
    );  

    request.responseType = 'json';

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
    this.resizeLoadedImage( nextImg );

    lastImg.parentNode.removeChild( lastImg );
    nextImg.classList.remove( 'loading' );

    nextImg.id = 'imgLast';

  } 


  resizeLoadedImage( image ){
    
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
    this.loadNextImage();
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
    
    this._loadJson(
      '/api/media/next',
      function( data ){
        thisRef.onNextImageData( data );
      }
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


  main(){
    // main entrypoint, call this when e.g. config load has finished
    let img = document.getElementById("imgLast");
    this.resizeLoadedImage( img );
    
    const thisRef = this;
    this._imageLoadedCallback = function(){
      thisRef.initClock();
    }
    this.loadNextImage();
  }


  init(){
    // bootstrap gifbox, load config before doing anything else
    const thisRef = this;
    this.loadConfig( function(){
      thisRef.main();
    });
  }

}


window.onload = function() {
    
    const gifbox = new GifBox();
    gifbox.init();

}