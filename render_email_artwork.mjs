// Render the normal desktop SCREEN design, never the separate print layout.
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
  await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:2,mobile:false});
  await call('Emulation.setEmulatedMedia',{media:'screen'});
  await call('Page.navigate',{url:pathToFileURL(join(issue,'raindrop.html')).href});
  await delay(500);
  const loaded=await call('Runtime.evaluate',{
    expression:`(async()=>{
      const specs=['400 16px Jost','500 16px Jost','600 16px Jost','700 16px Jost','italic 400 16px Jost'];
      for(const spec of specs){const faces=await document.fonts.load(spec);if(!faces.length||faces.some(f=>f.status!=='loaded'))throw Error('Required font did not load: '+spec);}
      await document.fonts.ready;
      await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      return [...document.images].filter(i=>!i.naturalWidth).map(i=>i.src);
    })()`,awaitPromise:true,returnByValue:true
  });
  if(loaded.exceptionDetails) throw Error('Font/image preparation failed: '+JSON.stringify(loaded.exceptionDetails));
  if(loaded.result.value.length) throw Error('Broken source images: '+loaded.result.value.join(', '));
  // Unroll scrolling only. Keep the screen CSS, content widths, fonts, and CTA direction.
  const prepared=await call('Runtime.evaluate',{returnByValue:true,awaitPromise:true,expression:`(async()=>{
    const selectors=['.bar .issue','.top .note p','.hero .sub','.item li','.foot .say'];
    const metrics=()=>selectors.map(selector=>{const el=document.querySelector(selector);if(!el)return null;const s=getComputedStyle(el);return {selector,width:el.getBoundingClientRect().width,font:s.fontFamily,size:s.fontSize,weight:s.fontWeight,lineHeight:s.lineHeight};});
    const before=metrics();
    const style=document.createElement('style');
    style.textContent='html,body{height:auto!important;overflow:visible!important}.page{height:auto!important;min-height:0!important;display:flex!important;flex-direction:column!important;overflow:visible!important}.scroll{flex:none!important;height:auto!important;max-height:none!important;overflow-y:scroll!important;overflow-x:hidden!important;scrollbar-gutter:stable!important}.foot{position:static!important}.nav,.dots,.edit-bar{visibility:hidden!important}';
    document.head.appendChild(style);
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const after=metrics();
    if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Unrolling changed screen typography or widths: '+JSON.stringify({before,after}));
    return {metrics:after,ctaDirection:getComputedStyle(document.querySelector('.foot .cta')).flexDirection};
  })()`});
  if(prepared.exceptionDetails) throw Error('Screen layout preservation failed: '+JSON.stringify(prepared.exceptionDetails));
  const measure=await call('Runtime.evaluate',{returnByValue:true,expression:`(()=>{
    const page=document.querySelector('.page').getBoundingClientRect();
    const foot=document.querySelector('.foot').getBoundingClientRect();
    const links=[...document.querySelectorAll('.foot .cta a')].map(a=>{const r=a.getBoundingClientRect();return {x:r.left-page.left,y:r.top-page.top,bottom:r.bottom-page.top,url:a.href,label:(a.textContent.trim()+' '+(a.querySelector('img')?.alt||'')).trim()};});
    const starts=[0,...['.stats','.mid','.lattice','.milestones'].map(s=>{const el=document.querySelector(s);return el?el.getBoundingClientRect().top-page.top:null;}).filter(y=>Number.isFinite(y)&&y>0&&y<foot.top-page.top),foot.top-page.top];
    return {x:page.x,y:page.y,width:page.width,height:page.height,footer:foot.top-page.top,starts:[...new Set(starts)].sort((a,b)=>a-b),links};
  })()`});
  const layout=measure.result.value;
  if(Math.abs(layout.width-1280)>1||!layout.links.length) throw Error('Invalid desktop screen layout: '+JSON.stringify(layout));
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
  const footerColumns=[];
  const footY=layout.starts.at(-1),footBottom=snap(layout.height),footHeight=footBottom-footY;
  const stacked=layout.links.length>1&&Math.abs(layout.links[0].x-layout.links[1].x)<1;
  if(stacked){
    const cut=snap(Math.min(...layout.links.map(a=>a.x)));
    const left=await capture('screen-footer-left.png',0,footY,cut,footHeight);
    left.href=null;left.alt='Rainmaker Securities private shares desk';
    footerColumns.push({width:cut,height:footHeight,parts:[left]});
    const ys=[footY,...layout.links.map(a=>snap(a.bottom)),footBottom];
    const parts=[];
    for(let i=0;i<ys.length-1;i++){
      if(ys[i+1]<=ys[i])continue;
      const part=await capture(`screen-footer-stack-${i}.png`,cut,ys[i],layout.width-cut,ys[i+1]-ys[i]);
      part.href=layout.links[i]?.url||null;part.alt=layout.links[i]?.label||'Rainmaker Securities';parts.push(part);
    }
    footerColumns.push({width:layout.width-cut,height:footHeight,parts});
  }else{
    const cuts=[0,...layout.links.map(a=>snap(a.x)),layout.width];
    for(let i=0;i<cuts.length-1;i++){
      const part=await capture(`screen-footer-row-${i}.png`,cuts[i],footY,cuts[i+1]-cuts[i],footHeight);
      part.href=i?layout.links[i-1].url:null;part.alt=i?layout.links[i-1].label:'Rainmaker Securities private shares desk';
      footerColumns.push({width:part.width,height:footHeight,parts:[part]});
    }
  }
  await writeFile(join(issue,'email','artwork-layout.json'),JSON.stringify({reference:'normal-screen',viewport:{width:1280,height:1000},width:layout.width,height:layout.height,bands,footerColumns,sourceMetrics:prepared.result.value},null,2));
  console.log('Normal screen artwork rendered: '+bands.length+' sections; CTA layout '+(stacked?'stacked':'horizontal')+' preserved');
} finally {
  socket?.close();child.kill();await delay(300);await rm(profile,{recursive:true,force:true});
}
