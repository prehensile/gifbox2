class Clock {
  
  constructor( imageRoot ){
    this._lastTimeString = "";
    this._imageRoot = imageRoot;
    this.onClockChange = null;
    this._interval = null;
  }


  _clockElement(){
    return document.getElementById( "clock" );
  }


  displayTime( digitString ){
    for (let i = 0; i < digitString.length; i++) {
        let ds = digitString[i];
        let img = document.getElementById( "img-" + i );
        img.src = this._imageRoot + ds + ".png"
    }
  }


  padNumber( num ){
    if( num < 10 ) return "0" + num;
    return "" + num;
  }

  
  flicker(){
    let clock = this._clockElement
    
    let op = clock.style.opacity;
    if( !op || op == "" ) op = 1.0;
    else op = parseFloat( op );
    
    const o = 0.5;
    clock.style.opacity = o + ((1.0-o)*Math.random());

    /*const jitter = 0.30;
    op += -(jitter/2) + (Math.random()*jitter);
    if( op > 1.0 ) op = 1.0;
    if( op < 0.0 ) op = 0.0;
    clock.style.opacity = op;*/
  }


  update(){
    let now = new Date();
    let timeString = this.padNumber( now.getHours() ) + this.padNumber( now.getMinutes() );
    if( timeString != this._lastTimeString ){
        this.displayTime( timeString );
        this._lastTimeString = timeString;
        if( this.onClockChange ){
          this.onClockChange();
        }
    }
    now = null;

    // this.flicker();
  }


  run(){
    const thisRef = this;
    this._interval = window.setInterval( function(){
        thisRef.update();
    }, 1000/12 );
    this.update();
  }


  stop(){
    if( this._interval ){
      window.clearInterval( this._interval )
      this._interval = null;
    }
  }


  show(){
    const clock = this._clockElement();
    clock.classList.remove( "hidden" );
  }


  hide(){
    const clock = this._clockElement();
    clock.classList.add( "hidden" );
  }

}