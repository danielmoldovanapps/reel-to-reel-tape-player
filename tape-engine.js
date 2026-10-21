/* Reel-to-Reel Tape Player — pitch-coupled transport, no time stretching.
 * Copyright (C) 2026 Daniel Moldovan aka [RO]Daniel.
 * SPDX-License-Identifier: GPL-3.0-only
 * Decodes to a Web Audio AudioBuffer and uses AudioBufferSourceNode playbackRate.
 * Real forward and reverse resampling: half speed = half pitch; 3x = 3x pitch.
 */
(function(global) {
'use strict';
class TapeAudio extends EventTarget {
  constructor() {
    super();
    this.preload='auto'; this._url=''; this._buffer=null; this._reverse=null; this._preview=null; this._reversePreview=null; this._trackDuration=NaN; this.useFastStart=false; this._previewLoading=null;
    this._ctx=null; this.output=null; this._source=null;
    this._time=0; this._at=0; this._speed=1; this._direction=1;
    this._paused=true; this._ended=false; this._volume=1;
    this._generation=0; this._sequence=0; this._loading=null;
    this._fetching=null; this._bytes=null;
    this._wantPlay=false; this.error=null;
    this._activeController=null;
  }
  setAudioContext(ctx) {
    if (this._ctx===ctx) return;
    if (this._ctx) throw new Error('Tape audio context already attached');
    this._ctx=ctx;
    this.output=ctx.createGain();
    this.output.gain.value=this._volume;
  }
  connect(node) { if (this.output) this.output.connect(node); }
  get src(){ return this._url; }
  set src(url){
    this._generation++; this._wantPlay=false;this._halt();
    if(this._activeController) this._activeController.abort();
    if(this._previewController) this._previewController.abort();
    this._url=String(url||'');this._buffer=null;this._reverse=null;this._preview=null;this._reversePreview=null;this._trackDuration=NaN;this._previewLoading=null;
    this._loading=null;this._fetching=null;this._bytes=null;
    this._time=0;this._ended=false;this._speed=1;this._direction=1;
    this.error=null;
  }
  removeAttribute(key){if(key==='src')this.src='';}
  get duration(){return this._buffer?this._buffer.duration:this._trackDuration;}
  get paused(){return this._paused;}
  get ended(){return this._ended;}
  get playbackRate(){return this._speed;}
  set playbackRate(v){
    v=Number(v);if(!Number.isFinite(v)||v<=0)throw new RangeError('Tape speed must be positive');
    this._sync();this._speed=v;
    if(this._source&&this._ctx){
      const p=this._source.playbackRate;
      p.cancelScheduledValues(this._ctx.currentTime);
      // Gentle resampling rate interpolation, NEVER pitch-correct/time-stretch.
      p.setTargetAtTime(v,this._ctx.currentTime,.016);
    }
  }
  get volume(){return this._volume;}
  set volume(v){this._volume=Math.min(1,Math.max(0,Number(v)||0));if(this.output)this.output.gain.value=this._volume;}
  get currentTime(){
    if(this._source&&!this._paused&&this._ctx){
      const current=this._time+this._direction*(this._ctx.currentTime-this._at)*this._speed;
      return Math.max(0,Math.min(this.duration||0,current));
    }
    return this._time;
  }
  set currentTime(value){
    const max=this.duration;
    const sec=Math.max(0,Math.min(Number.isFinite(max)?max:Infinity,Number(value)||0));
    this._time=sec;this._ended=false;
    if(this._source&&!this._paused){this._halt(false);this._startSource();}
    this.dispatchEvent(new Event('seeked'));
  }
  _sync(){if(this._source&&!this._paused){this._time=this.currentTime;this._at=this._ctx.currentTime;}}
  _halt(markPaused=true){
    const source=this._source;
    if(markPaused){this._paused=true;this._wantPlay=false;}
    this._source=null;
    if(source){
      source.onended=null;
      try{source.stop();}catch(_e){}
      try{source.disconnect();}catch(_e){}
    }
  }
  // For large files served by ReelPlayer, fetch a small PCM preview first.
  // The full decoder runs in parallel; no HTMLMediaElement or time stretching.
  _canPreview(){return this.useFastStart && /^\/file\/\d+\?/.test(this._url);}
  async _loadPreview(){
    if(this._preview)return this._preview;
    if(this._previewLoading)return this._previewLoading;
    if(!this._canPreview() || !this._ctx)return null;
    const id=this._generation, url=this._url.replace(/^\/file\//,'/preview/');
    const ctrl=new AbortController();
    // Keep preview and full-track requests independently cancellable.
    this._previewController=ctrl;
    this._previewLoading=(async()=>{
      try{
        const r=await fetch(url,{signal:ctrl.signal,cache:'no-store'});
        if(!r.ok)throw new Error('Fast-start preview unavailable');
        const duration=Number(r.headers.get('X-Reel-Duration'));
        const data=await r.arrayBuffer();
        if(id!==this._generation)return null;
        const b=await this._ctx.decodeAudioData(data);
        if(id!==this._generation || this._buffer)return null;
        this._preview=b;
        this._trackDuration=(Number.isFinite(duration)&&duration>0)?duration:b.duration;
        return b;
      }catch(e){
        // Optional preview: normal full-track decode always remains usable.
        if(e.name!=='AbortError')console.warn('Reel fast-start preview skipped:',e.message);
        return null;
      }
    })();
    return this._previewLoading;
  }
  // Fetch compressed song bytes as soon as a track is selected. This needs
  // no AudioContext/user gesture, so the native desktop-open handshake and
  // WebKit audio startup can overlap the file transfer.
  async _fetchData(){
    if(this._bytes)return this._bytes;
    if(this._fetching)return this._fetching;
    if(!this._url)return null;
    const id=this._generation;
    const controller=new AbortController();this._activeController=controller;
    const fetching=(async()=>{
      const response=await fetch(this._url,{signal:controller.signal});
      if(!response.ok)throw new Error('Cannot read audio ('+response.status+')');
      const bytes=await response.arrayBuffer();
      if(id!==this._generation)return null;
      this._bytes=bytes;
      return bytes;
    })();
    this._fetching=fetching;
    // The background request must not generate an unhandled rejection when
    // a user skips a track before its data has arrived.
    fetching.catch(()=>{});
    return fetching;
  }
  load(){
    if(!this._url)return Promise.resolve();
    if(this._loading)return this._loading;
    // Preload bytes before the first user Play creates AudioContext. Keep the
    // request alive without leaking an unhandled rejection if the file changes.
    if(!this._ctx){if(!this._canPreview())this._fetchData().catch(()=>{});return Promise.resolve();}
    const id=this._generation;
    this._loading=(async()=>{
      try{
        const bytes=await this._fetchData();
        if(!bytes || id!==this._generation)return;
        const buffer=await this._ctx.decodeAudioData(bytes);
        if(id!==this._generation)return;
        this._buffer=buffer;
        this._trackDuration=buffer.duration;
        // The preview is retained only until its source reaches the handoff.
        if(!this._source || this._source.buffer!==this._preview){
          this._preview=null;this._reversePreview=null;
          if(this._previewController)this._previewController.abort();
        }
        // Release the compressed file and the completed fetch Promise (which
        // otherwise retains its ArrayBuffer result for long mixes).
        this._bytes=null;this._fetching=null;
        this.dispatchEvent(new Event('loadedmetadata'));
      }catch(e){
        if(id===this._generation && e.name!=='AbortError'){
          this.error=e;console.error('Reel playback decode failed:',e);
          this.dispatchEvent(new Event('error'));
        }
        throw e;
      }
    })();
    this._loading.catch(()=>{});
    return this._loading;
  }
  async play(){
    this._wantPlay=true;
    const generation=this._generation;
    const sequence=++this._sequence;
    if(!this._ctx)throw new Error('Audio engine has not been initialized');
    try{
      // Context activation and full-track decoding are independent. Starting
      // both in parallel avoids adding their startup latencies together.
      const full=this._buffer?Promise.resolve(this._buffer):this.load();
      // A preview can start the source while full-length decoding continues.
      const ready=this._canPreview() ? Promise.race([
        full,
        this._loadPreview().then(preview=>preview||full)
      ]) : full;
      const activated=this._ctx.state==='running'?Promise.resolve():this._ctx.resume();
      await Promise.all([ready,activated]);
      if(generation!==this._generation||!this._wantPlay||sequence!==this._sequence)return;
      if(!this._source){this._paused=false;this._ended=false;this._startSource();}
    }catch(e){if(generation===this._generation){this._paused=true;}throw e;}
  }
  pause(){
    this._sequence++;this._sync();this._halt();
  }
  setDirection(direction){
    const value=direction<0?-1:1;
    if(value===this._direction)return;
    this._sync();this._halt(false);this._direction=value;
    if((this._buffer||this._preview)&&!this._paused)this._startSource();
  }
  get direction(){return this._direction;}
  _makeReverseBuffer(buffer){
    const isPreview=buffer===this._preview;
    if(isPreview&&this._reversePreview)return this._reversePreview;
    if(!isPreview&&this._reverse)return this._reverse;
    if(!buffer)throw new Error('No tape loaded');
    // Reverse PCM samples, not HTML seeking; rewind plays BACKWARDS with pitch.
    const b=buffer, channels=b.numberOfChannels, frames=b.length;
    const result=this._ctx.createBuffer(channels,frames,b.sampleRate);
    for(let ch=0;ch<channels;ch++){
      const input=b.getChannelData(ch), output=result.getChannelData(ch);
      for(let i=0,j=frames-1;i<frames;i++,j--)output[i]=input[j];
    }
    if(isPreview)this._reversePreview=result;
    else this._reverse=result;
    return result;
  }
  _startSource(){
    if(!this._ctx||(!this._buffer&&!this._preview)||this._paused)return;
    const base=this._buffer||this._preview;
    const isPreview=base===this._preview;
    const buf=this._direction<0?this._makeReverseBuffer(base):base;
    const duration=base.duration;
    const offset=this._direction<0?duration-this._time:this._time;
    if(offset>=duration-.00001){
      // A preview boundary is not the end of the song. Wait for the normal
      // full decoder if necessary; resume at the real sample position.
      if(isPreview){
        this._time=duration;
        this._paused=true;
        this.load().then(()=>{
          if(!this._wantPlay||!this._buffer)return;
          this._paused=false;this._startSource();
        }).catch(()=>{});
        return;
      }
      this._paused=true;this._ended=true;
      this.dispatchEvent(new Event('ended'));return;
    }
    const src=this._ctx.createBufferSource();
    src.buffer=buf;
    src.playbackRate.value=this._speed;
    src.connect(this.output);
    const sequence=++this._sequence;
    this._source=src;
    this._at=this._ctx.currentTime;
    this._time=Math.min(duration,Math.max(0,this._time));
    src.onended=()=>{
      if(this._source!==src||this._paused||sequence!==this._sequence)return;
      if(isPreview && this._direction>0){
        // Hand over to the full PCM source at the preview boundary, keeping
        // the absolute tape position and existing pitch/transport state.
        this._time=duration;
        this._source=null;
        this._at=this._ctx.currentTime;
        if(this._buffer){this._preview=null;this._reversePreview=null;this._startSource();}
        else{
          this._paused=true;
          this.load().then(()=>{
            if(!this._wantPlay||!this._buffer)return;
            this._paused=false;this._preview=null;this._reversePreview=null;
            this._startSource();
          }).catch(()=>{});
        }
        return;
      }
      this._time=this._direction<0?0:duration;
      this._source=null;this._paused=true;this._wantPlay=false;this._ended=true;
      this.dispatchEvent(new Event('ended'));
    };
    src.start(0,Math.max(0,offset));
  }
}
global.TapeAudio=TapeAudio;
})(window);
