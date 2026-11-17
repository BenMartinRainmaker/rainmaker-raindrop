// Render the original print composition into contiguous, email-safe PNG sections.
// Only the generated PNGs are delivered in email; no browser code is embedded.
import {spawn} from 'node:child_process';
import {mkdtemp, readFile, writeFile, mkdir, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';

const issue=resolve(process.argv[2]);
const chrome=process.env.CHROME || (process.platform==='darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : 'google-chrome');
const profile=await mkdtemp(join(tmpdir(),'raindrop-artwork-'));
const assets=join(issue,'email','assets');
await mkdir(assets,{recursive:true});
const args=['--headless=new','--disable-gpu','--hide-scrollbars','--remote-debugging-port=0',`--user-data-dir=${profile}`];
if(process.platform==='linux') args.push('--no-sandbox');
const child=spawn(chrome,args,{stdio:'ignore'});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let socket;
try {
  let port;
  for(let i=0;i<150;i++) {
    try {port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}
    catch {await delay(100);}
  }
  if(!port) throw Error('Chrome debugger did not start');
  const target=await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  socket=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((ok,fail)=>{socket.onopen=ok;socket.onerror=fail;});
  let next=0;
  const pending=new Map();
  socket.onmessage=e=>{
    const message=JSON.parse(e.data),p=pending.get(message.id);
    if(p){pending.delete(message.id);message.error?p.fail(Error(JSON.stringify(message.error))):p.ok(message.result);}
  };
  const call=(method,params={})=>new Promise((ok,fail)=>{
    const id=++next;pending.set(id,{ok,fail});socket.send(JSON.stringify({id,method,params}));
  });
  await call('Page.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:816,height:1056,deviceScaleFactor:2,mobile:false});
  await call('Emulation.setEmulatedMedia',{media:'print'});
  await call('Page.navigate',{url:pathToFileURL(join(issue,'raindrop.html')).href});
  await delay(500);
  const loaded=await call('Runtime.evaluate',{
    expression:`(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));return [...document.images].filter(i=>!i.naturalWidth).map(i=>i.src)})()`,awaitPromise:true,returnByValue:true
  });
  if(loaded.result.value.length) throw Error('Broken source images: '+loaded.result.value.join(', '));
  const measure=await call('Runtime.evaluate',{returnByValue:true,expression:`(()=>{
    const page=document.querySelector('.page').getBoundingClientRect();
    const foot=document.querySelector('.foot').getBoundingClientRect();
    const links=[...document.querySelectorAll('.foot .cta a')].map(a=>({x:a.getBoundingClientRect().left-page.left,url:a.href,label:a.textContent.trim()}));
    const starts=[0,...['.stats','.mid','.lattice','.milestones'].map(s=>document.querySelector(s)?.getBoundingClientRect().top-page.top).filter(y=>Number.isFinite(y)&&y>0&&y<foot.top-page.top),foot.top-page.top];
    return {x:page.x,y:page.y,width:page.width,height:page.height,footer:foot.top-page.top,starts:[...new Set(starts)].sort((a,b)=>a-b),links};
  })()`});
  const layout=measure.result.value;
  if(Math.abs(layout.width-816)>1||layout.height>1057) throw Error('Original must be one Letter page: '+JSON.stringify(layout));
  // Snap all section boundaries to the same physical pixel grid. No gaps or overlaps.
  const snap=n=>Math.round(n*2)/2;
  layout.starts=layout.starts.map(snap);
  const capture=async(file,x,y,width,height)=>{
    const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:layout.x+x,y:layout.y+y,width,height,scale:1}});
    await writeFile(join(assets,file),Buffer.from(shot.data,'base64'));
    return {file,width,height};
  };
  const bands=[];
  for(let i=0;i<layout.starts.length-1;i++) {
    const y=layout.starts[i],height=layout.starts[i+1]-y;
    bands.push(await capture(`page-section-${i}.png`,0,y,layout.width,height));
  }
  const cuts=[0,...layout.links.map(a=>snap(a.x)),layout.width];
  const footer=[];
  for(let i=0;i<cuts.length-1;i++) {
    const part=await capture(`page-footer-${i}.png`,cuts[i],layout.starts.at(-1),cuts[i+1]-cuts[i],snap(layout.height)-layout.starts.at(-1));
    part.href=i ? layout.links[i-1].url : null;
    part.alt=i ? layout.links[i-1].label : 'Rainmaker Securities private shares desk';
    footer.push(part);
  }
  await writeFile(join(issue,'email','artwork-layout.json'),JSON.stringify({width:layout.width,height:layout.height,bands,footer},null,2));
  console.log('Original artwork rendered: '+bands.length+' page sections and '+footer.length+' linked footer sections');
} finally {
  socket?.close();child.kill();await delay(300);await rm(profile,{recursive:true,force:true});
}
