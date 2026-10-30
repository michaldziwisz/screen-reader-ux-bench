import {voiceOver as vo} from '@guidepup/guidepup';
import {spawn,execFileSync} from 'node:child_process';
import fs from 'node:fs';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await vo.start({capture:'initial',timeout:20000});
try {
 for(const variant of ['GRUPY','PLASKI']) {
  const p=spawn('out/Catalyst/Build/Products/Debug-maccatalyst/UXBench.app/Contents/MacOS/UXBench',[variant]);
  const r={variant,evidence:'live_reader_macos_catalyst_NOT_iOS',steps:[]};
  try{
   await wait(4000);
   r.tree=JSON.parse(execFileSync('out/probe',[String(p.pid),'activate','tree'],{encoding:'utf8'}));
   if(r.tree.front_pid!==p.pid)throw Error('Catalyst activation failed');
   for(let i=0;i<26;i++){
    await vo.clearSpokenPhraseLog();
    await vo.press(i===0?'Meta+i':'Tab',{capture:'initial'});
    r.steps.push({kind:i===0?'anchor':'Tab',item:await vo.itemText(),phrases:await vo.spokenPhraseLog(),after:JSON.parse(execFileSync('out/probe',[String(p.pid)],{encoding:'utf8'}))});
   }
   r.positive=r.steps.some(s=>s.phrases.join(' ').includes('Imię'));
   if(!r.positive)throw Error('Positive control failed');
  }catch(e){r.error=String(e);process.exitCode=1;}
  finally{fs.writeFileSync(`out/catalyst-${variant}.json`,JSON.stringify(r,null,2));p.kill('SIGTERM');}
 }
}finally{await vo.stop();}
