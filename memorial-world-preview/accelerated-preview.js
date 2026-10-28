/* Explicit owner-controlled mode: remains accelerated until this setting is changed. */
(() => {
  const PREVIEW_ENABLED = true;
  if(!PREVIEW_ENABLED) return;
  let frame = 0, remaining = 15, paused = false, started = false, targets = [], map = null;
  const viewport = document.querySelector('#viewport');
  const toolbar = document.createElement('div');
  toolbar.className='timeline-actions';
  toolbar.style.cssText='justify-content:center;margin:12px 0;flex-wrap:wrap';
  toolbar.innerHTML='<button class="button outline" id="previousPreview">← Previous picture</button><button class="button" id="pausePreview">Pause preview</button><button class="button outline" id="nextPreview">Next picture →</button>';
  document.querySelector('.reveal').after(toolbar);
  document.querySelector('.reveal .eyebrow').textContent='Accelerated preview · Sample portraits';
  document.querySelector('.reveal h2').textContent='Next transformation in…';
  document.querySelector('.reveal p').textContent='Every 15 seconds · A demonstration of the future daily reveal';
  document.querySelector('.edition-head .badge').textContent='Preview · Changes every 15 seconds';
  document.querySelector('.hero .eyebrow').textContent='Many little photos. One changing picture.';
  document.querySelector('.hero > p').textContent='Your photo, someone you love, or your treasured pet—one tiny piece of a giant photo mosaic. Free for everyone to explore.';
  document.querySelector('.art-note').textContent='Accelerated demonstration: a small fictional photo collection repeats and is rearranged, alongside Bruce and Henry’s two real founding photos, to illustrate different sample portraits. No new purchases or live AI generation are occurring. The future daily format begins only when the owner chooses to switch.';
  const faq=document.querySelector('.faq details p');
  faq.textContent='This accelerated preview cycles through sample portraits every 15 seconds. Pause or inspect the individual photos at your own pace. It does not simulate real payments, new contributors or a live archive. The intended daily service would hold each edition for 24 hours. Switching to that service requires an explicit owner decision and the production publishing system.';
  document.querySelector('#playHistory').textContent='▶ Compare sample editions';
  function indexAt(col,row) {
    const s=editions[stageIndex], i=row*s.cols+col, person=people.find(p=>p.id===i+1);
    return person ? person.tile : map ? map[i] : (i*13+row*7)%sourceImages.length;
  }
  window.picturepurdleTileIndex=indexAt;
  function refreshLabels() {
    document.querySelector('#stageTitle').textContent='Picturepurdle · Accelerated sample '+(frame+1)+' of '+(targets.length||4);
    document.querySelector('#countdown').textContent='00:'+String(remaining).padStart(2,'0');
    const inspecting=scale>1 || document.querySelector('#photoDialog').open;
    document.querySelector('.edition-head .badge').textContent=paused?'Preview paused':inspecting?'Inspecting photos · Timer held':'Preview · Next picture in '+remaining+'s';
    document.querySelector('#revealDate').textContent=!started?'Preparing sample portraits…':paused?'Preview paused · Use Next picture to explore':inspecting?'Timer held while you inspect photos · ↺ returns to the portrait':'Sample portraits only · Future editions will be daily';
    document.querySelector('#stageDescription').textContent='Illustrative sample editions, not a real dated archive. The accelerated portrait preview is separate from these two sample photo counts.';
  }
  function paintPortrait(target) {
    const s=editions[stageIndex], mini=document.createElement('canvas');mini.width=s.cols;mini.height=s.rows;
    const m=mini.getContext('2d',{willReadFrequently:true}),ratio=canvas.width/canvas.height;
    let sw=target.width,sh=target.height;if(sw/sh>ratio)sw=sh*ratio;else sh=sw/ratio;
    m.drawImage(target,(target.width-sw)/2,(target.height-sh)/2,sw,sh,0,0,s.cols,s.rows);
    const pixels=m.getImageData(0,0,s.cols,s.rows).data;
    const sampler=document.createElement('canvas');sampler.width=8;sampler.height=8;
    const sc=sampler.getContext('2d',{willReadFrequently:true});
    const palette=sourceImages.slice(0,16).map(image=>{sc.clearRect(0,0,8,8);sc.drawImage(image,0,0,8,8);const p=sc.getImageData(0,0,8,8).data;let r=0,g=0,b=0;for(let i=0;i<p.length;i+=4){r+=p[i];g+=p[i+1];b+=p[i+2];}return[r/64,g/64,b/64];});
    map=new Uint8Array(s.count);
    const w=canvas.width/s.cols,h=canvas.height/s.rows;
    for(let i=0;i<s.count;i++) {
      let best=Infinity,index=0;
      for(let j=0;j<palette.length;j++) {
        const p=palette[j],dr=p[0]-pixels[i*4],dg=p[1]-pixels[i*4+1],db=p[2]-pixels[i*4+2];
        // Small deterministic variation avoids long runs of identical tiles.
        const score=dr*dr*.3+dg*dg*.59+db*db*.11+((i*17+j*29+frame*11)%47)*16;
        if(score<best){best=score;index=j;}
      }
      const person=people.find(p=>p.id===i+1);if(person)index=person.tile;
      map[i]=index;
      const x=i%s.cols*w,y=Math.floor(i/s.cols)*h;
      ctx.drawImage(sourceImages[index],x,y,w,h);
      ctx.fillStyle=`rgba(${pixels[i*4]},${pixels[i*4+1]},${pixels[i*4+2]},.68)`;
      ctx.fillRect(x,y,w+.15,h+.15);
    }
    transform();detail(selected||people[0]);
  }
  const baseRender=render;
  render=async function(){await baseRender();if(!targets.length)targets=[targetImages[0],targetImages[1],sourceImages[2],sourceImages[7]];paintPortrait(targets[frame]);started=true;refreshLabels();};
  async function advance(direction=1) {
    if(busy || !started) return;
    playing=false;
    const old=document.createElement('canvas');old.width=canvas.width;old.height=canvas.height;old.getContext('2d').drawImage(canvas,0,0);
    frame=(frame+direction+targets.length)%targets.length;remaining=15;scale=1;tx=ty=0;
    await render();
    if(!matchMedia('(prefers-reduced-motion: reduce)').matches) {
      old.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3';viewport.append(old);
      old.animate([{opacity:1},{opacity:0}],{duration:1100,easing:'ease-in-out'}).finished.then(()=>old.remove());
    }
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
