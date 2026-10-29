/* Explicit owner-controlled mode: remains accelerated until this setting is changed. */
(() => {
  const PREVIEW_ENABLED = true;
  const REVEAL_SECONDS = 45;
  const BLEND_DURATION_MS = 4000;
  let transitioning = false, activeBlend = null, activeIncoming = null;
  const CHANGE_PERCENT_PER_REVEAL = 9;
  const STEPS_TO_CHANGE = Math.ceil(100 / CHANGE_PERCENT_PER_REVEAL);
  const PREVIEW_VARIANTS = STEPS_TO_CHANGE * 2;
  let naturalTarget=null;
  let paintedFrame=-1, paintedStage=-1, samplePreparation=null;
  const originalSamples=Array.from({length:16},(_,i)=>i), freshSamples=[];
  const atlasPromise=img('sample-portraits-atlas-v2.jpg');
  async function prepareSamplePhotos() {
    if(!samplePreparation)samplePreparation=(async()=>{
      const atlas=await atlasPromise, urls=[];
      const crop=document.createElement('canvas');crop.width=320;crop.height=320;
      const c=crop.getContext('2d');
      for(let row=0;row<4;row++)for(let col=0;col<4;col++){
        c.clearRect(0,0,320,320);
        c.drawImage(atlas,col*atlas.width/4,row*atlas.height/4,atlas.width/4,atlas.height/4,0,0,320,320);
        urls.push(crop.toDataURL('image/jpeg',.94));
      }
      const photos=await Promise.all(urls.map(img));
      photos.forEach((photo,i)=>{freshSamples.push(sourceImages.length);sourceImages.push(photo);DATA.tiles.push(urls[i]);});
    })();
    await samplePreparation;
  }
  function tileBucket(i) {let h=Math.imul(i+1,0x45d9f3b);h^=h>>>16;return(h>>>0)%10;}

  const naturalPromise=img("natural-portrait-v2.jpg");
  if(!PREVIEW_ENABLED) return;
  let frame = 0, remaining = REVEAL_SECONDS, paused = false, started = false, targets = [], map = null, lastStage = -1;
  const viewport = document.querySelector('#viewport');
  const toolbar = document.createElement('div');
  toolbar.className='timeline-actions';
  toolbar.style.cssText='justify-content:center;margin:12px 0;flex-wrap:wrap';
  toolbar.innerHTML='<button class="button outline" id="previousPreview">← Previous picture</button><button class="button" id="pausePreview">Pause preview</button><button class="button outline" id="nextPreview">Next picture →</button>';
  document.querySelector('.reveal').after(toolbar);
  document.querySelector('.reveal .eyebrow').textContent='Accelerated preview · Sample portraits';
  document.querySelector('.reveal h2').textContent='Next small change in…';
  document.querySelector('.reveal p').textContent='Every 45 seconds: a gentle fade, an evolving face, and refreshed sample photos';
  document.querySelector('.edition-head .badge').textContent='Preview · Changes every 45 seconds';
  document.querySelector('.hero .eyebrow').textContent='Many little photos. One changing picture.';
  document.querySelector('.hero > p').textContent='Your photo, someone you love, or your treasured pet—one tiny piece of a giant photo mosaic. Free for everyone to explore.';
  document.querySelector('.art-note').textContent="The big picture changes. All of your photos remain forever in the mosaic. This preview changes a little every 45 seconds. Later, we plan to reveal one new big picture each day. Pay once, with no yearly renewal. Photo placement lasts for as long as Picturepurdle operates. This preview doesn’t accept payments or public photo submissions.";
  const faq=document.querySelector('.faq details p');
  faq.textContent="You’re viewing a preview. For now, the picture changes a little every 45 seconds so you can see the idea in action. Later, we plan to reveal one new big picture each day and leave it on display for 24 hours. The big picture changes. All of your photos remain forever in the mosaic. Pay once, with no yearly renewal. Photo placement lasts for as long as Picturepurdle operates. Payments and public photo submissions aren’t available in this preview.";
  document.querySelector('#playHistory').textContent='▶ Compare sample editions';
  function indexAt(col,row) {
    const s=editions[stageIndex], i=row*s.cols+col, person=people.find(p=>p.id===i+1);
    return person ? person.tile : map ? map[i] : (i*13+row*7)%sourceImages.length;
  }
  window.picturepurdleTileIndex=indexAt;
  function refreshLabels() {
    document.querySelector('#stageTitle').textContent='Picturepurdle · Accelerated sample '+(frame+1)+' of '+PREVIEW_VARIANTS;
    document.querySelector('#countdown').textContent='00:'+String(remaining).padStart(2,'0');
    const inspecting=scale>1 || document.querySelector('#photoDialog').open;
    document.querySelector('.edition-head .badge').textContent=paused?'Preview paused':inspecting?'Inspecting photos · Timer held':transitioning?'Changing now · Gentle 4-second fade':'Preview · Next small change in '+remaining+'s';
    document.querySelector('#revealDate').textContent=!started?'Preparing sample portraits…':paused?'Preview paused · Use Next picture to explore':inspecting?'Timer held while you inspect photos · ↺ returns to the portrait':transitioning?'Watch the portrait gently fade into its next version':'Sample portraits only · Future editions will be daily';
    document.querySelector('#stageDescription').textContent='Illustrative sample editions, not a real dated archive. The accelerated portrait preview is separate from these two sample photo counts.';
  }
  function paintPortrait(target,nextTarget,blend) {
    const s=editions[stageIndex], mini=document.createElement('canvas');mini.width=s.cols;mini.height=s.rows;
    const m=mini.getContext('2d',{willReadFrequently:true}),ratio=canvas.width/canvas.height;
    function drawPortrait(image,alpha) {
      let sw=image.width,sh=image.height;if(sw/sh>ratio)sw=sh*ratio;else sh=sw/ratio;
      m.globalAlpha=alpha;
      m.drawImage(image,(image.width-sw)/2,(image.height-sh)/2,sw,sh,0,0,s.cols,s.rows);
      m.globalAlpha=1;
    }
    // Closely registered natural portraits; never geometrically distort either image.
    drawPortrait(targets[0],1);
    const step=frame<=STEPS_TO_CHANGE?frame:PREVIEW_VARIANTS-frame;
    const progress=Math.min(1,step*CHANGE_PERCENT_PER_REVEAL/100);
    if(progress>0)drawPortrait(naturalTarget,progress);
    const pixels=m.getImageData(0,0,s.cols,s.rows).data;
    const sampler=document.createElement('canvas');sampler.width=8;sampler.height=8;
    const sc=sampler.getContext('2d',{willReadFrequently:true});
    const sampleIndices=originalSamples.concat(freshSamples);
    const palette=sampleIndices.map(index=>{const image=sourceImages[index];sc.clearRect(0,0,8,8);sc.drawImage(image,0,0,8,8);const p=sc.getImageData(0,0,8,8).data;let r=0,g=0,b=0;for(let i=0;i<p.length;i+=4){r+=p[i];g+=p[i+1];b+=p[i+2];}return {index,rgb:[r/64,g/64,b/64]};});
    const sameStage=paintedStage===stageIndex && map && map.length===s.count;
    const previous=sameStage?map:null;
    const newFrame=paintedFrame!==frame;
    map=previous?previous.slice():new Uint8Array(s.count);
    const bucket=(frame+9)%10;
    let refreshed=0;
    const w=canvas.width/s.cols,h=canvas.height/s.rows;
    for(let i=0;i<s.count;i++) {
      const person=people.find(p=>p.id===i+1);
      const replace=previous && newFrame && !person && tileBucket(i)===bucket;
      let index=previous?previous[i]:0;
      if(!previous || replace) {
        let best=Infinity;
        for(const entry of palette) {
          if(replace?!freshSamples.includes(entry.index):!originalSamples.includes(entry.index))continue;
          if(replace && entry.index===previous[i])continue;
          const p=entry.rgb,dr=p[0]-pixels[i*4],dg=p[1]-pixels[i*4+1],db=p[2]-pixels[i*4+2];
          const score=dr*dr*.3+dg*dg*.59+db*db*.11+((i*17+entry.index*29+frame*11)%47)*16;
          if(score<best){best=score;index=entry.index;}
        }
        if(replace && index!==previous[i])refreshed++;
      }
      if(person)index=person.tile;
      map[i]=index;
      const x=i%s.cols*w,y=Math.floor(i/s.cols)*h;
      ctx.drawImage(sourceImages[index],x,y,w,h);
      ctx.fillStyle=`rgba(${pixels[i*4]},${pixels[i*4+1]},${pixels[i*4+2]},.68)`;
      ctx.fillRect(x,y,w+.15,h+.15);
    }
    paintedFrame=frame;paintedStage=stageIndex;
    viewport.dataset.temporaryTilesRefreshed=String(refreshed);
    viewport.dataset.previewFrame=String(frame);
    viewport.dataset.previewTilePool=String(sampleIndices.length);
    transform();detail(selected||people[0]);
  }
  function finishBlend() {
    if(activeBlend)activeBlend.finish();
    if(activeIncoming)activeIncoming.finish();
  }
  // Finding a photo ends any portrait fade before zooming into the tiles.
  const locateBeforePreview=locate;
  locate=function(person,doZoom=true) {
    playing=false;
    finishBlend();
    locateBeforePreview(person,doZoom);
    refreshLabels();
  };
  const baseRender=render;
  render=async function(){if(!started || lastStage!==stageIndex){await baseRender();lastStage=stageIndex;}if(!targets.length)targets=[targetImages[0],targetImages[1],sourceImages[2],sourceImages[7]];busy=true;try{if(!naturalTarget)naturalTarget=await naturalPromise;await prepareSamplePhotos();paintPortrait(targets[0],targets[0],0);started=true;}finally{busy=false;}refreshLabels();};
  async function advance(direction=1) {
    if(busy || !started || transitioning) return;
    playing=false;
    const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
    const old=document.createElement('canvas');
    old.width=canvas.width;old.height=canvas.height;
    old.getContext('2d').drawImage(canvas,0,0);
    // Cover the current portrait BEFORE repainting so the new step never flashes.
    old.setAttribute('aria-hidden','true');
    old.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3;transform-origin:0 0';
    old.style.transform=canvas.style.transform;
    viewport.append(old);
    transitioning=true;
    try {
      const total=PREVIEW_VARIANTS;
      frame=(frame+direction+total)%total;remaining=REVEAL_SECONDS;
      await render();
      if(!reducedMotion) {
        // Fade out the old view and bring in the new one with a gentle lightening
        // at the midpoint. The expensive mosaic is still rendered only once.
        const timing={duration:BLEND_DURATION_MS,easing:'ease-in-out',fill:'forwards'};
        activeBlend=old.animate([{opacity:1,offset:0},{opacity:0.1,offset:0.5},{opacity:0,offset:1}],timing);
        activeIncoming=canvas.animate([{opacity:0,offset:0},{opacity:0.45,offset:0.5},{opacity:1,offset:1}],timing);
        await Promise.all([activeBlend.finished,activeIncoming.finished]);
      }
    } finally {
      old.remove();
      if(activeIncoming)activeIncoming.cancel();
      if(activeBlend)activeBlend.cancel();
      activeIncoming=null;activeBlend=null;transitioning=false;refreshLabels();
    }
  }
  // Show the current tiles immediately when someone starts exploring the picture.
  for(const event of ['pointerdown','wheel','keydown']) {
    viewport.addEventListener(event,()=>{finishBlend();},{passive:true});
  }
  document.querySelector('#previousPreview').onclick=()=>advance(-1);
  document.querySelector('#nextPreview').onclick=()=>advance(1);
  document.querySelector('#pausePreview').onclick=e=>{paused=!paused;e.target.textContent=paused?'Resume preview':'Pause preview';refreshLabels();};
  document.querySelector('#playHistory').addEventListener('click',()=>{paused=true;document.querySelector('#pausePreview').textContent='Resume preview';});
  document.querySelectorAll('[data-stage]').forEach(b=>b.addEventListener('click',()=>{paused=true;document.querySelector('#pausePreview').textContent='Resume preview';}));
  setInterval(()=>{
    if(!started){if(sourceImages.length && !busy)render();refreshLabels();return;}
    if(!paused && !busy && scale===1 && !document.querySelector('#photoDialog').open && !document.hidden) {remaining--;if(remaining<=0)advance();}
    refreshLabels();
  },1000);
  refreshLabels();
})();
