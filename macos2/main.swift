import AppKit

final class Folder: NSObject {
 let name:String; let children:[Folder]
 init(_ name:String,_ children:[Folder]=[]) {self.name=name;self.children=children}
}
final class Bench:NSObject,NSApplicationDelegate,NSTableViewDataSource,NSTableViewDelegate,NSOutlineViewDataSource,NSOutlineViewDelegate {
 var window:NSWindow!; let search=NSTextField();let table=NSTableView();let outline=NSOutlineView();let details=NSTextView();let status=NSTextField(labelWithString:"Gotowe")
 let roots=[Folder("Dokumenty",[Folder("Umowy",[Folder("Najem"),Folder("Praca")]),Folder("Faktury",[Folder("2025"),Folder("2026"),Folder("Korekty")]),Folder("Raporty")]),Folder("Zdjęcia",[Folder("Wakacje"),Folder("Rodzina")]),Folder("Muzyka")]
 let columns=CommandLine.arguments.contains("STAN") ? ["Stan","Rozmiar","Data","Nazwa"] : ["Nazwa","Data","Rozmiar","Stan"]
 var last="";var events:[[String:Any]]=[];var clock:Timer?
 func log(_ kind:String,_ data:Any) {events.append(["time":Date().timeIntervalSince1970,"kind":kind,"data":data])}
 func id(_ v:NSView,_ name:String,_ label:String) {v.identifier=NSUserInterfaceItemIdentifier(name);v.setAccessibilityIdentifier(name);v.setAccessibilityLabel(label)}
 func group(_ title:String,_ frame:NSRect)->NSView {let v=NSView(frame:frame);v.setAccessibilityElement(true);v.setAccessibilityRole(.group);id(v,"group_"+title,title);return v}
 func applicationDidFinishLaunching(_ n:Notification) {
  window=NSWindow(contentRect:NSRect(x:40,y:40,width:1200,height:780),styleMask:[.titled,.closable,.resizable],backing:.buffered,defer:false);window.title="UXPomiar2"
  let root=NSView(frame:NSRect(x:0,y:0,width:1200,height:780));window.contentView=root
  let tools=group("Narzędzia",NSRect(x:10,y:710,width:1180,height:60));root.addSubview(tools)
  for (i,name) in ["Nowy","Otwórz","Zapisz","Usuń","Kopiuj","Wklej"].enumerated() {let b=NSButton(title:name,target:nil,action:nil);b.frame=NSRect(x:i*90,y:12,width:86,height:32);id(b,"button_\(i)",name);tools.addSubview(b)}
  search.frame=NSRect(x:560,y:14,width:340,height:28);id(search,"search","Szukaj");tools.addSubview(search)
  let split=NSSplitView(frame:NSRect(x:10,y:190,width:1180,height:510));split.isVertical=true;split.dividerStyle = .thin;id(split,"split","Foldery i pliki");root.addSubview(split)
  let folders=group("Foldery",NSRect(x:0,y:0,width:280,height:510));let files=group("Pliki",NSRect(x:281,y:0,width:899,height:510));split.addSubview(folders);split.addSubview(files)
  let oc=NSTableColumn(identifier:NSUserInterfaceItemIdentifier("folder"));oc.title="Folder";outline.addTableColumn(oc);outline.outlineTableColumn=oc;outline.headerView=nil;outline.dataSource=self;outline.delegate=self;outline.rowHeight=25;id(outline,"outline","Foldery");outline.allowsEmptySelection=false
  let os=NSScrollView(frame:folders.bounds);os.autoresizingMask=[.width,.height];os.hasVerticalScroller=true;os.documentView=outline;folders.addSubview(os)
  for name in columns {let col=NSTableColumn(identifier:NSUserInterfaceItemIdentifier(name));col.title=name;col.width=name=="Nazwa" ? 275:170;col.isEditable=false;table.addTableColumn(col)}
  table.dataSource=self;table.delegate=self;table.rowHeight=23;table.allowsMultipleSelection=false;table.allowsEmptySelection=false;id(table,"table","Pliki")
  let ts=NSScrollView(frame:files.bounds);ts.autoresizingMask=[.width,.height];ts.hasVerticalScroller=true;ts.hasHorizontalScroller=true;ts.documentView=table;files.addSubview(ts)
  let dg=group("Szczegóły",NSRect(x:10,y:35,width:1180,height:145));root.addSubview(dg)
  let ds=NSScrollView(frame:NSRect(x:0,y:0,width:800,height:145));ds.hasVerticalScroller=true;details.frame=ds.bounds;details.isEditable=false;details.isSelectable=true;details.string=detailsText;details.font=NSFont.systemFont(ofSize:15);id(details,"details","Szczegóły");ds.documentView=details;dg.addSubview(ds)
  status.frame=NSRect(x:10,y:4,width:1180,height:26);id(status,"status","Stan operacji");root.addSubview(status)
  window.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true);table.selectRowIndexes(IndexSet(integer:0),byExtendingSelection:false);outline.selectRowIndexes(IndexSet(integer:0),byExtendingSelection:false);window.makeFirstResponder(search)
  NSEvent.addLocalMonitorForEvents(matching:.keyDown) {e in self.log("key",["code":e.keyCode,"flags":e.modifierFlags.rawValue]);return e}
  clock=Timer.scheduledTimer(withTimeInterval:0.06,repeats:true) {_ in self.poll()}
 }
 func numberOfRows(in t:NSTableView)->Int {records.count}
 func tableView(_ t:NSTableView,viewFor col:NSTableColumn?,row:Int)->NSView? {let f=NSTextField(labelWithString:records[row][col!.identifier.rawValue]!);id(f,"cell_\(row)_\(col!.identifier.rawValue)",records[row][col!.identifier.rawValue]!);return f}
 func tableViewSelectionDidChange(_ n:Notification) {log("selection",table.selectedRow)}
 func outlineView(_ o:NSOutlineView,numberOfChildrenOfItem item:Any?)->Int {(item as? Folder)?.children.count ?? roots.count}
 func outlineView(_ o:NSOutlineView,child index:Int,ofItem item:Any?)->Any {(item as? Folder)?.children[index] ?? roots[index]}
 func outlineView(_ o:NSOutlineView,isItemExpandable item:Any)->Bool {!(item as! Folder).children.isEmpty}
 func outlineView(_ o:NSOutlineView,viewFor col:NSTableColumn?,item:Any)->NSView? {let f=NSTextField(labelWithString:(item as! Folder).name);id(f,"folder_"+(item as! Folder).name,(item as! Folder).name);return f}
 func outlineViewSelectionDidChange(_ n:Notification){log("folder",(outline.item(atRow:outline.selectedRow) as? Folder)?.name ?? "")}
 func poll() {
  guard let data=try? Data(contentsOf:URL(fileURLWithPath:"out/command.json")),let c=(try? JSONSerialization.jsonObject(with:data)) as? [String:Any],let seq=c["seq"] as? String,seq != last else {return};last=seq
  let cmd=c["command"] as? String ?? ""
  if cmd=="focus" {let target=c["target"] as? String ?? "";let v:NSResponder=target=="table" ? table : target=="outline" ? outline : target=="details" ? details : search;window.makeFirstResponder(v)}
  if cmd=="reset-table" {table.selectRowIndexes(IndexSet(integer:0),byExtendingSelection:false);window.makeFirstResponder(table)}
  if cmd=="reset-tree" {outline.collapseItem(nil,collapseChildren:true);outline.selectRowIndexes(IndexSet(integer:0),byExtendingSelection:false);window.makeFirstResponder(outline)}
  if cmd=="emit" {
   let mode=c["mode"] as? String ?? "plain";let count=c["count"] as? Int ?? 1
   let priority:NSAccessibilityPriorityLevel=mode=="low" ? .low : mode=="medium" ? .medium : .high
   for i in 1...count {let text=count==1 ? "Kontrola komunikatu \(mode)" : "Plik \(i) z 5 skopiowany";status.stringValue=text;log("emit",["mode":mode,"text":text]);if mode != "plain" {NSAccessibility.post(element:status,notification:.announcementRequested,userInfo:[.announcement:text,.priority:priority.rawValue])}}
  }
  log("command",c)
  let state:[String:Any]=["seq":seq,"tableSelected":table.selectedRow,"outlineSelected":outline.selectedRow,"outlineRows":outline.numberOfRows,"detailsSelection":[details.selectedRange().location,details.selectedRange().length],"firstResponder":String(describing:window.firstResponder),"events":events]
  try? JSONSerialization.data(withJSONObject:state,options:[.prettyPrinted,.sortedKeys]).write(to:URL(fileURLWithPath:"out/state.json"),options:.atomic)
 }
}
let app=NSApplication.shared;let delegate=Bench();app.delegate=delegate;app.setActivationPolicy(.regular);app.run()
