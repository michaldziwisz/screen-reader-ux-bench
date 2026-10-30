import {voiceOver as vo} from '@guidepup/guidepup';
import {spawn,execFile,execFileSync} from 'node:child_process';
import {promisify} from 'node:util';
const execAsync=promisify(execFile);
async function rawVO(property){return (await execAsync('osascript',['-e',`tell application "VoiceOver" to return ${property}`],{timeout:5000})).stdout.trim();}
import fs from 'node:fs';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const probe=(pid,tree=false)=>JSON.parse(execFileSync('out/probe',[String(pid),...(tree?['tree']:[])],{encoding:'utf8',timeout:5000}));
// Guidepup capture odpytuje dopiero PO akcji. Dla serii potrzebny jest odczyt równoległy.
async function sampleDuring(fn){
 const samples=[];const baseline=await rawVO('content of last phrase');let done=false;let error=null;
 const start=performance.now();const action=fn().then(()=>{done=true;},e=>{error=e;done=true;});
 while(!done || performance.now()-start<1600){
  const t=performance.now();try{samples.push({ms:t-start,text:await rawVO('content of last phrase')});}catch(e){samples.push({ms:t-start,error:String(e)});}
  await wait(40);
 }
 await action;if(error)throw error;
 let previous=baseline;const phrases=[];
 for(const x of samples){if(x.text && x.text!==previous){phrases.push(x.text);previous=x.text;}}
 return {baseline,samples,phrases,method:'concurrent last-phrase polling; lower bound, not speech queue'};
}
let seq=0;
async function command(data){const c={...data,seq:String(++seq)};fs.writeFileSync('out/command.tmp',JSON.stringify(c));fs.renameSync('out/command.tmp','out/command.json');for(let i=0;i<80;i++){await wait(60);try{const s=JSON.parse(fs.readFileSync('out/state.json'));if(s.seq===c.seq)return s;}catch{}}throw Error('IPC acknowledgement missing');}
let started=false;
try{
 await vo.start({capture:'initial',timeout:20000});started=true;
 fs.writeFileSync('out/voiceover-settings.json',JSON.stringify({version:vo.version,settings:await vo.getSettings()},null,2));
 for(const variant of ['NAZWA','STAN']){
  const proc=spawn('out/UXBench.app/Contents/MacOS/UXBench',[variant],{stdio:['ignore','ignore',fs.openSync(`out/${variant}-stderr.log`,'w')]});
  const r={variant,evidence:'live_reader',steps:[],error:null};
  const save=()=>fs.writeFileSync(`out/${variant}.json`,JSON.stringify(r,null,2));
  try{
   await wait(2500);r.tree=probe(proc.pid,true);
   async function step(kind,fn,full=false){
    const before=probe(proc.pid);if(before.front_pid!==proc.pid && !/voiceover/i.test(before.front_bundle))throw Error('PID gate '+JSON.stringify(before));
    await vo.clearSpokenPhraseLog();
    let captureResult=null;
    if(full)captureResult=await sampleDuring(fn);else await fn();
    const phrases=full?captureResult.phrases:await vo.spokenPhraseLog();const item=full?await rawVO('text under cursor of vo cursor'):await vo.itemText();
    const entry={kind,phrases,item,captureResult,words:phrases.join(' ').trim().split(/\s+/u).filter(Boolean).length,after:probe(proc.pid),app:await command({command:'state'})};
    r.steps.push(entry);save();return entry;
   }
   const key=(kind,k)=>step(kind,()=>vo.press(k,{capture:'initial'}));
   const focus=target=>step('focus-'+target,()=>command({command:'focus',target}).then(()=>wait(400)),true);
   await focus('search');const positive=await key('positive-reader','Control+Alt+F3');r.positive=positive.phrases.join(' ').includes('Szukaj');if(!r.positive)throw Error('Positive reader control failed');
   r.rawCaptureControl=await sampleDuring(async()=>{await command({command:'focus',target:'details'});await wait(1200);await command({command:'focus',target:'search'});await wait(1200);});
   if(!r.rawCaptureControl.phrases.some(x=>x.includes('Szukaj')))throw Error('Raw VoiceOver capture control failed');
   for(let i=0;i<20;i++)await key('Tab-cycle','Tab');
   await focus('details');for(let i=0;i<16;i++){const x=await key('details-to-search:Tab','Tab');if(x.after.focus?.AXIdentifier==='search')break;}
   for(const k of ['F6','Control+F6','Shift+F6']){await focus('details');for(let i=0;i<3;i++)await key('area:'+k,k);}
   await step('reset-tree',()=>command({command:'reset-tree'}).then(()=>wait(300)),true);
   for(const k of ['ArrowRight','ArrowDown','ArrowRight','ArrowDown','ArrowDown','ArrowLeft','ArrowLeft','End','Home'])await key('outline:'+k,k);
   r.expanded_tree=probe(proc.pid,true);
   await step('reset-table',()=>command({command:'reset-table'}).then(()=>wait(400)),true);
   for(let i=0;i<4;i++)await key('table:ArrowDown','ArrowDown');
   await key('table:VO-in','Control+Alt+Shift+ArrowDown');
   for(const k of ['ArrowRight','ArrowRight','ArrowDown','ArrowLeft','ArrowDown','ArrowUp'])await key('table:VO-'+k,'Control+Alt+'+k);
   r.table_tree=probe(proc.pid,true);
   await key('table:VO-out','Control+Alt+Shift+ArrowUp');
   await step('reset-table-tab',()=>command({command:'reset-table'}).then(()=>wait(300)),true);
   for(let i=0;i<90;i++){const x=await key('table-exit:Tab','Tab');if(x.after.focus?.AXIdentifier==='details')break;}
   await focus('details');await key('details:read','Control+Alt+F3');
   for(const k of ['ArrowDown','ArrowDown','ArrowDown','Meta+ArrowUp','ArrowDown'])await key('details:'+k,k);
   await focus('search');await key('areas:VO-top','Control+Alt+Home');
   let previous='';const entered=new Set();
   for(let i=0;i<35;i++){const s=await key('areas:VO-right','Control+Alt+ArrowRight');if(s.item===previous)await key('areas:VO-out','Control+Alt+Shift+ArrowUp');else if(/group|split|table|outline|scroll area/i.test(s.item)&&!entered.has(s.item)){entered.add(s.item);await key('areas:VO-in','Control+Alt+Shift+ArrowDown');}previous=s.item;}
   await focus('search');await key('rotor:open','Control+Alt+u');for(let i=0;i<4;i++)await key('rotor:next-category','ArrowRight');await key('rotor:close','Escape');
   await focus('search');await wait(2000);
   for(const mode of ['plain','low','medium','high']){
    await step('single:'+mode,()=>command({command:'emit',mode,count:1}).then(()=>wait(6000)),true);
    for(let repeat=1;repeat<=6;repeat++){await key('burst-baseline','Control+Alt+F3');await step(`burst:${mode}:${repeat}`,()=>command({command:'emit',mode,count:5}).then(()=>wait(8000)),true);}
   }
   const paced=await step('positive-paced-announcements',async()=>{for(let i=1;i<=5;i++){await command({command:'emit',mode:'high',count:1,text:`Kontrola ${i} z 5`});await wait(3000);}},true);
   r.announcementCapturePositive=[1,2,3,4,5].every(i=>paced.phrases.some(p=>p.includes(`Kontrola ${i} z 5`)));
   if(!r.announcementCapturePositive)throw Error('Announcement capture control failed');
   await key('positive-reader-after','Control+Alt+F3');
   execFileSync('screencapture',['-x',`out/${variant}.png`]);
  }catch(e){r.error=String(e);process.exitCode=1;}
  finally{save();proc.kill('SIGTERM');await wait(500);}
 }
}finally{if(started)await vo.stop();}
