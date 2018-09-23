

class GifBox {
  
  constructor(){
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

    let request = new XMLHttpRequest();  
    
    request.open(
        'GET',
        'http://localhost:5000/api/media/next',
        true
    );  

    request.responseType = 'json';

    request.onreadystatechange = function (oEvent) {  
      if (request.readyState === 4) {  
        if (request.status === 200) {  
          thisRef.onNextImageData( request.response )
        } else {  
          console.log( "Error", request.statusText );  
        }  
      }  
    };  

    request.send();  
      
  }


  run(){
    let img = document.getElementById("imgLast");
    this.resizeLoadedImage( img );

    this.loadNextImage();
  }

}


window.onload = function() {
    
    var gifbox = new GifBox();
    gifbox.run();

    //var clock = new Clock( "images/clock/lcd-" );
    var clock = new Clock( "images/clock/digit-" );
    clock.run();

}