(async function(){
const owner = window.GHPAGES_REPO_OWNER;
const repo = window.GHPAGES_REPO_NAME;
const dir = window.IMAGES_DIR || "images";
if(!owner || !repo){
console.error("Set window.GHPAGES_REPO_OWNER and window.GHPAGES_REPO_NAME in index.html");
return;
}


const api = `https://api.github.com/repos/${owner}/${repo}/contents/${dir}`;
const res = await fetch(api, { headers: { 'Accept':'application/vnd.github.v3+json' }});
if(!res.ok){ console.error('Failed to list images from', api); return; }
const files = (await res.json()).filter(f => /\.(png|jpe?g|gif|webp|avif)$/i.test(f.name));
files.sort((a,b)=> a.name.localeCompare(b.name));
const slides = document.getElementById('slides');


// Preload and render
for(const f of files){
const img = new Image();
img.loading = 'lazy';
img.src = f.download_url; // public raw URL from GitHub API
img.alt = f.name;
slides.appendChild(img);
}


let idx = 0; let timer = null;
const prev = document.getElementById('prev');
const next = document.getElementById('next');
const play = document.getElementById('play');
const pause= document.getElementById('pause');
const intervalInput = document.getElementById('interval');


function go(i){
const count = slides.children.length;
if(!count) return;
idx = (i+count)%count;
const pct = -100*idx;
slides.style.transform = `translateX(${pct}%)`;
}


function start(){
stop();
const s = Math.max(1, parseInt(intervalInput.value||'4',10));
timer = setInterval(()=> go(idx+1), s*1000);
}
function stop(){ if(timer){ clearInterval(timer); timer=null; } }


prev.addEventListener('click', ()=> go(idx-1));
next.addEventListener('click', ()=> go(idx+1));
play.addEventListener('click', start);
pause.addEventListener('click', stop);


// Keyboard nav
window.addEventListener('keydown', (e)=>{
if(e.key==='ArrowLeft') go(idx-1);
if(e.key==='ArrowRight') go(idx+1);
if(e.key===' ') { if(timer) stop(); else start(); }
});


// Auto start after initial render
const onImagesReady = () => { if(slides.children.length) { go(0); start(); } };
if(document.readyState !== 'loading') onImagesReady(); else document.addEventListener('DOMContentLoaded', onImagesReady);
})();
