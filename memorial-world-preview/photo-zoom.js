/* Picturepurdle: redraw visible photographic tiles from source images. */
(() => {
  const viewport = document.querySelector('#viewport');
  const closeup = document.createElement('canvas');
  closeup.id = 'photoCloseup';
  closeup.setAttribute('aria-hidden', 'true');
  closeup.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;display:none';
  viewport.insertBefore(closeup, document.querySelector('#selectedTile'));
  const css = document.createElement('style');
  css.textContent = '.mosaic-explainer{max-width:780px;margin:0 auto 24px;text-align:center}.mosaic-explainer h2{font-size:clamp(24px,4vw,35px);margin-bottom:10px}.mosaic-explainer p{color:#526e83;font-size:15px}.mosaic-explainer button{margin:7px}#photoDialog{border:1px solid #b8d5e4;border-radius:18px;padding:24px;max-width:min(430px,90vw);color:#123d54;background:white}#photoDialog::backdrop{background:#123d5470}#photoDialog img{display:block;width:100%;max-height:55vh;object-fit:contain;border-radius:9px}#photoDialog button{margin-top:14px}.photo-help{font-size:13px;color:#426b80;text-align:center;margin:12px 0}.viewport{touch-action:none}#photoCloseup{z-index:1}.pin,.selected-tile{z-index:2}.selected-tile{object-fit:cover}';
  document.head.append(css);
  const explain = document.createElement('section');
  explain.className = 'mosaic-explainer';
  explain.innerHTML = '<h2>Your photo. One piece of a much bigger picture.</h2><p>Add yourself, someone you love, or your pet. Each photo becomes a tiny tile in a giant portrait. Together, everyone’s pictures create the face you see.</p><button class="button" id="explorePhotos">See the little photos ↗</button><p class="hint">Working preview: a small fictional photo collection repeats. No real contributions or payments yet.</p>';
  document.querySelector('.edition-head').before(explain);
  const help = document.createElement('p');
  help.className = 'photo-help';
  help.textContent = 'Zoom in to see individual photos. Drag to explore. Tap a tile to open its original sample photo.';
  document.querySelector('.frame').after(help);
  const dialog = document.createElement('dialog');
  dialog.id = 'photoDialog';
  dialog.setAttribute('aria-labelledby', 'photoDialogTitle');
  dialog.innerHTML = '<h3 id="photoDialogTitle">A photo inside the picture</h3><img id="originalTilePhoto" alt="Original fictional sample photo"><p id="tileAddress"></p><p class="hint">Fictional sample, repeated in this demonstration. This is not a purchased contribution.</p><form method="dialog"><button class="button">Close photo</button></form>';
  document.body.append(dialog);
  dialog.addEventListener('click', event => { if(event.target === dialog) dialog.close(); });
  function tileIndex(col, row) {
    if(window.picturepurdleTileIndex) return window.picturepurdleTileIndex(col,row);
    const id = row * editions[stageIndex].cols + col + 1;
    const person = people.find(p => p.id === id);
    return person ? person.tile : ((id - 1) * 13 + row * 7) % sourceImages.length;
  }
  function redrawPhotos() {
    if(scale < 4 || !sourceImages.length) { closeup.style.display = 'none'; return; }
    const width = viewport.clientWidth, height = viewport.clientHeight;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const bw = Math.round(width * dpr), bh = Math.round(height * dpr);
    if(closeup.width !== bw || closeup.height !== bh) {closeup.width = bw;closeup.height = bh;}
    closeup.style.display = 'block';
    const c = closeup.getContext('2d');
    c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, width, height);
    const edition = editions[stageIndex], tw = width * scale / edition.cols, th = height * scale / edition.rows;
    const left = Math.max(0, Math.floor(-tx / tw)), right = Math.min(edition.cols - 1, Math.floor((width - tx) / tw));
    const top = Math.max(0, Math.floor(-ty / th)), bottom = Math.min(edition.rows - 1, Math.floor((height - ty) / th));
    c.imageSmoothingEnabled = true; c.imageSmoothingQuality = 'high';
    closeup.style.opacity = Math.min(1, (scale - 2) / 6);
    for(let row = top;row <= bottom;row++) for(let col = left;col <= right;col++) {
      if(row * edition.cols + col >= edition.count) continue;
      const x = tx + col * tw, y = ty + row * th;
      const image=sourceImages[tileIndex(col,row)], ratio=tw/th; let sw=image.width, sh=image.height; if(sw/sh>ratio) sw=sh*ratio; else sh=sw/ratio; c.drawImage(image,(image.width-sw)/2,(image.height-sh)/2,sw,sh,x,y,tw+.25,th+.25);
      if(scale >= 16) {c.strokeStyle = '#ffffffb3';c.lineWidth = 1;c.strokeRect(x,y,tw,th);}
    }
  }
  const originalTransform = transform;
  transform = function() { originalTransform(); redrawPhotos(); };
  detail = function(person) {
    if(!sourceImages.length) return;
    const c = document.querySelector('#detail').getContext('2d'), p = position(person.id), edition = editions[stageIndex];
    c.clearRect(0,0,600,600);
    for(let y = -1;y <= 1;y++) for(let x = -1;x <= 1;x++) {
      const col = p.col + x, row = p.row + y;
      if(col < 0 || col >= edition.cols || row < 0 || row * edition.cols + col >= edition.count) continue;
      c.drawImage(sourceImages[tileIndex(col,row)],(x+1)*200,(y+1)*200,200,200);
    }
    c.strokeStyle='#00a5cf'; c.lineWidth=8; c.strokeRect(202,202,196,196);
    document.querySelector('#detailLabel').textContent='Original sample photos in this tile’s neighborhood. The center photo is outlined in blue. Photos repeat in this demo.';
  };
  function openTile(col,row) {
    const edition = editions[stageIndex];
    if(col<0 || col>=edition.cols || row<0 || row*edition.cols+col>=edition.count) return;
    document.querySelector('#originalTilePhoto').src=DATA.tiles[tileIndex(col,row)];
    document.querySelector('#tileAddress').textContent='Sample edition #'+edition.number+' · Row '+(row+1)+' · Column '+(col+1)+' · Simulated spot '+(row*edition.cols+col+1).toLocaleString();
    dialog.showModal();
  }
  document.querySelector('#explorePhotos').onclick=()=>{
    zoom(32);
    viewport.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
    help.textContent='These are the original sample photos. Drag to explore, tap any tile to open it, or use ↺ to return to the giant portrait.';
  };
  let press=null;
  viewport.addEventListener('pointerdown',e=>{press={x:e.clientX,y:e.clientY};});
  viewport.addEventListener('pointerup',e=>{
    if(!press || Math.hypot(e.clientX-press.x,e.clientY-press.y)>8) {press=null;return;}
    press=null;
    if(scale<8) {zoom(32);return;}
    const box=viewport.getBoundingClientRect(), edition=editions[stageIndex];
    openTile(Math.floor((e.clientX-box.left-tx)/(viewport.clientWidth*scale/edition.cols)),Math.floor((e.clientY-box.top-ty)/(viewport.clientHeight*scale/edition.rows)));
  });
  viewport.addEventListener('pointercancel',()=>press=null);
  viewport.addEventListener('keydown',e=>{
    if(e.key==='Enter' || e.key===' ') {e.preventDefault();if(scale<8) zoom(32);else {const s=editions[stageIndex];openTile(Math.floor((viewport.clientWidth/2-tx)/(viewport.clientWidth*scale/s.cols)),Math.floor((viewport.clientHeight/2-ty)/(viewport.clientHeight*scale/s.rows)));}}
    const moves={ArrowLeft:[100,0],ArrowRight:[-100,0],ArrowUp:[0,100],ArrowDown:[0,-100]};
    if(moves[e.key]) {e.preventDefault();tx+=moves[e.key][0];ty+=moves[e.key][1];transform();}
  });
  viewport.setAttribute('aria-label','Photo mosaic. Press Enter to zoom into sample photos, use arrow keys to pan, and Enter again to open the center tile.');
  window.addEventListener('resize',()=>{transform();});
})();
