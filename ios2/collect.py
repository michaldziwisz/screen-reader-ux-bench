"""Zbieraj jedynie własne dzienniki z izolowanego runnera Simulatora."""
from pathlib import Path
import shutil,os
if os.environ.get('CI')!='true':raise SystemExit('CI only')
out=Path('out/app-runtime');out.mkdir(parents=True,exist_ok=True)
for i,p in enumerate((Path.home()/'Library/Developer/CoreSimulator/Devices').glob('*/data/Containers/Data/Application/*/Documents/bench2-*.json')):
 shutil.copy2(p,out/(str(i)+'-'+p.name))
print('runtime files',len(list(out.glob('*.json'))))
