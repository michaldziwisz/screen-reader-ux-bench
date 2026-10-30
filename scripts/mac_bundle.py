import plistlib
from pathlib import Path
p=Path("out/UXBench.app/Contents/Info.plist")
p.write_bytes(plistlib.dumps({"CFBundleIdentifier":"org.uxbench.mac","CFBundleName":"UXBench","CFBundleExecutable":"UXBench","CFBundlePackageType":"APPL","NSHighResolutionCapable":True}))
