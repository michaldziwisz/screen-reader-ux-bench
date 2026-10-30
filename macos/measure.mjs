import {voiceOver as vo} from '@guidepup/guidepup';
import {spawn,execFileSync} from 'node:child_process';
import fs from 'node:fs';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const key=k=>vo.press(k,{capture:'initial'});
fs.mkdirSync('out',{recursive:true});
const probe=(pid,tree=false)=>JSON.parse(execFileSync('out/probe',[String(pid),...(tree?['tree']:[])],{encoding:'utf8',timeout:5000}));
let started=false;
try {
 await vo.start({capture:"initial",timeout:20000});started=true;
 fs.writeFileSync('out/voiceover-settings.json',JSON.stringify({version:vo.version,settings:await vo.getSettings()},null,2));
 for (const variant of ['GRUPY','PLASKI']) {
  const proc=spawn('out/UXBench.app/Contents/MacOS/UXBench',[variant],{stdio:['ignore','ignore','pipe']});
  const r={variant,evidence:'live_reader',version:vo.version,steps:[],probe:[],error:null};
  const save=()=>fs.writeFileSync(`out/${variant}.json`,JSON.stringify(r,null,2));
  try {
   await wait(2500);
   r.tree=probe(proc.pid,true);
   async function step(kind,fn) {
    const before=probe(proc.pid);if(before.front_pid!==proc.pid && !/voiceover/i.test(before.front_bundle))throw Error('PID gate: unexpected foreground '+JSON.stringify(before));
    await vo.clearSpokenPhraseLog();
    const t=performance.now();await fn();const elapsed=performance.now()-t;
    const phrases=await vo.spokenPhraseLog();
    const item=await vo.itemText();
    const entry={kind,phrases,item,words:phrases.join(' ').trim().split(/\s+/u).filter(Boolean).length,api_elapsed_ms:elapsed,after:probe(proc.pid)};
    r.steps.push(entry);save();return entry;
   }
   // Kontrola dodatnia: własne pole z rozpoznawalną polską etykietą.
   await step('anchor',()=>key('Meta+i'));
   await step('probe',()=>key('Control+Alt+F3'));
   r.positive=r.steps.some(x=>x.phrases.join(' ').includes('Imię'));
   if(!r.positive) throw Error('Positive speech control failed');
   for(let i=0;i<36;i++)await step('Tab',()=>key('Tab'));
   if(new Set(r.steps.filter(s=>s.kind==='Tab').map(s=>s.after.focus?.AXIdentifier)).size<6)throw Error('Tab positive movement control failed');
   await step('anchor-VO',()=>key('Meta+i'));
   let previousItem='';const entered=new Set();
   for(let i=0;i<50;i++){
    const s=await step('VO+Right',()=>key('Control+Alt+ArrowRight'));
    if(s.item===previousItem) await step('VO+Shift+Up',()=>key('Control+Alt+Shift+ArrowUp'));
    else if(/group|table|scroll area/i.test(s.item) && !entered.has(s.item)) {entered.add(s.item);await step('VO+Shift+Down',()=>key('Control+Alt+Shift+ArrowDown'));}
    if(s.item==='Zapisz jako plik button')break;
    previousItem=s.item;
   }
   await step('shortcut-save',()=>key('Meta+s'));
   await step('shortcut-dialog',()=>key('Meta+k'));
   r.dialog_before=probe(proc.pid,true);
   await step('Escape-dialog',()=>key('Escape'));
   r.dialog_after=probe(proc.pid,true);
   execFileSync('screencapture',['-x',`out/${variant}.png`]);
  }catch(e){r.error=String(e);process.exitCode=1;}
  finally {save();proc.kill('SIGTERM');await wait(600);}
 }
}finally {if(started)await vo.stop();}
