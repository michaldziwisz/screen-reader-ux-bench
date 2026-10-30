import {voiceOver as vo} from '@guidepup/guidepup';
import {spawn,execFileSync} from 'node:child_process';
import fs from 'node:fs';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync('out',{recursive:true});
const probe=(pid,tree=false)=>JSON.parse(execFileSync('out/probe',[String(pid),...(tree?['tree']:[])],{encoding:'utf8',timeout:5000}));
let started=false;
try {
 await vo.start({capture:true,timeout:20000});started=true;
 fs.writeFileSync('out/voiceover-settings.json',JSON.stringify({version:vo.version,settings:await vo.getSettings()},null,2));
 for (const variant of ['GRUPY','PLASKI']) {
  const proc=spawn('out/UXBench.app/Contents/MacOS/UXBench',[variant],{stdio:['ignore','ignore','pipe']});
  const r={variant,evidence:'live_reader',version:vo.version,steps:[],probe:[],error:null};
  const save=()=>fs.writeFileSync(`out/${variant}.json`,JSON.stringify(r,null,2));
  try {
   await wait(2500);
   r.tree=probe(proc.pid,true);
   async function step(kind,fn) {
    const before=probe(proc.pid);if(before.front_pid!==proc.pid)throw Error('PID gate: application not foreground');
    await vo.clearSpokenPhraseLog();
    const t=performance.now();await fn();const elapsed=performance.now()-t;
    const phrases=await vo.spokenPhraseLog();
    const item=await vo.itemText();
    const entry={kind,phrases,item,words:phrases.join(' ').trim().split(/\s+/u).filter(Boolean).length,api_elapsed_ms:elapsed,after:probe(proc.pid)};
    r.steps.push(entry);save();return entry;
   }
   // Kontrola dodatnia: własne pole z rozpoznawalną polską etykietą.
   await step('anchor',()=>vo.press('Meta+i',{capture:true}));
   await step('probe',()=>vo.perform(vo.keyboardCommands.describeItem,{capture:true}));
   r.positive=r.steps.some(x=>x.phrases.join(' ').includes('Imię'));
   if(!r.positive) throw Error('Positive speech control failed');
   for(let i=0;i<36;i++)await step('Tab',()=>vo.press('Tab',{capture:true}));
   await step('anchor-VO',()=>vo.press('Meta+i',{capture:true}));
   for(let i=0;i<50;i++){
    const s=await step('VO+Right',()=>vo.next({capture:true}));
    if(/group|table|scroll area/i.test(s.item)) await step('VO+Shift+Down',()=>vo.interact({capture:true}));
   }
   await step('shortcut-save',()=>vo.press('Meta+s',{capture:true}));
   await step('shortcut-dialog',()=>vo.press('Meta+k',{capture:true}));
   r.dialog_before=probe(proc.pid,true);
   await step('Escape-dialog',()=>vo.press('Escape',{capture:true}));
   r.dialog_after=probe(proc.pid,true);
   execFileSync('screencapture',['-x',`out/${variant}.png`]);
  }catch(e){r.error=String(e);process.exitCode=1;}
  finally {save();proc.kill('SIGTERM');await wait(600);}
 }
}finally {if(started)await vo.stop();}
