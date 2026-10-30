import {voiceOver} from '@guidepup/guidepup';
import fs from 'node:fs';
const result={};
try {
 await voiceOver.start({captureSpokenPhrases:true});
 result.version=voiceOver.version;
 await voiceOver.next();
 result.phrases=await voiceOver.spokenPhraseLog();
 result.item=await voiceOver.itemText();
} catch(e) { result.error=String(e); process.exitCode=1; }
finally {fs.writeFileSync('out/voiceover-scout.json',JSON.stringify(result,null,2)); await voiceOver.stop().catch(()=>{});}
