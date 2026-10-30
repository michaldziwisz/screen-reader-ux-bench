import AppKit

final class App: NSObject, NSApplicationDelegate {
 var window:NSWindow!
 var first:NSTextField!
 var radios:[NSButton]=[]
 let grouped = !CommandLine.arguments.contains("PLASKI")
 func applicationDidFinishLaunching(_ n:Notification) {
  let root=NSStackView();root.orientation = .vertical;root.alignment = .leading;root.spacing=6
  root.edgeInsets=NSEdgeInsets(top:12,left:20,bottom:12,right:20)
  var controls:[String:NSView]=[:]
  func field(_ id:String,_ title:String,_ value:String="") -> NSView {
   let stack=NSStackView();stack.orientation = .horizontal
   let lab=NSTextField(labelWithString:title);lab.setAccessibilityElement(false)
   let f=NSTextField(string:value);f.identifier=NSUserInterfaceItemIdentifier(id);f.setAccessibilityLabel(title)
   f.widthAnchor.constraint(equalToConstant:350).isActive=true
   stack.addArrangedSubview(lab);stack.addArrangedSubview(f)
   if id=="imie" {first=f}
   return stack
  }
  func button(_ id:String,_ title:String,_ sel:Selector) -> NSView {
   let b=NSButton(title:title,target:self,action:sel);b.bezelStyle = .rounded;b.identifier=NSUserInterfaceItemIdentifier(id);b.setAccessibilityLabel(title);return b
  }
  controls["imie"]=field("imie","Imię")
  controls["nazw"]=field("nazw","Nazwisko")
  controls["szt"]=field("szt","Liczba sztuk","1")
  let rg=NSStackView();rg.orientation = .horizontal;rg.setAccessibilityRole(.group);rg.setAccessibilityLabel("Sposób dostawy")
  for (i,name) in ["Kurier","Paczkomat","Odbiór osobisty"].enumerated() {
   let b=NSButton(radioButtonWithTitle:name,target:self,action:#selector(selectRadio(_:)));b.tag=i;b.identifier=NSUserInterfaceItemIdentifier("sposob_\(i)");b.state=i==0 ? .on:.off;radios.append(b);rg.addArrangedSubview(b)
  }
  controls["sposob"]=rg
  let country=NSPopUpButton();country.addItems(withTitles:["Polska","Czechy","Niemcy","Słowacja"]);country.setAccessibilityLabel("Kraj");country.identifier=NSUserInterfaceItemIdentifier("kraj");controls["kraj"]=country
  for (id,name) in [("faktura","Wystaw fakturę"),("news","Zapisz na newsletter")] {
   let b=NSButton(checkboxWithTitle:name,target:nil,action:nil);b.identifier=NSUserInterfaceItemIdentifier(id);controls[id]=b
  }
  let scroll=NSScrollView();scroll.hasVerticalScroller=true
  let table=NSTableView();table.addTableColumn(NSTableColumn(identifier:NSUserInterfaceItemIdentifier("zamowienia")));table.headerView=nil;table.dataSource=self;table.delegate=self;table.rowHeight=22;table.setAccessibilityLabel("Ostatnie zamówienia");table.identifier=NSUserInterfaceItemIdentifier("lista")
  scroll.documentView=table;scroll.heightAnchor.constraint(equalToConstant:140).isActive=true;scroll.widthAnchor.constraint(equalToConstant:500).isActive=true;controls["lista"]=scroll
  controls["zapisz"]=button("zapisz","Zapisz zamówienie",#selector(save))
  controls["anuluj"]=button("anuluj","Anuluj",#selector(cancel))
  controls["komunikat"]=button("komunikat","Pokaż komunikat",#selector(dialog))
  controls["plik"]=button("plik","Zapisz jako plik",#selector(file))
  func add(_ s:NSStackView,_ ids:[String]) { for id in ids {s.addArrangedSubview(controls[id]!)} }
  if grouped {
   for (name,ids) in [("Dane odbiorcy",["imie","nazw"]),("Dostawa",["sposob","kraj","szt"]),("Opcje",["faktura","news","lista"])] {
    let box=NSBox();box.title=name;box.setAccessibilityLabel(name)
    let st=NSStackView();st.orientation = .vertical;st.alignment = .leading;st.spacing=6;add(st,ids)
    box.contentView=st;root.addArrangedSubview(box)
   }
   add(root,["zapisz","anuluj","komunikat","plik"])
  } else { add(root,["zapisz","lista","nazw","news","szt","komunikat","imie","sposob","anuluj","kraj","faktura","plik"]) }
  window=NSWindow(contentRect:NSRect(x:100,y:60,width:740,height:850),styleMask:[.titled,.closable,.resizable],backing:.buffered,defer:false)
  window.title="UXPomiar \(grouped ? "GRUPY":"PLASKI")";window.contentView=root
  let menu=NSMenu();let item=NSMenuItem();let sub=NSMenu()
  for (name,action,key) in [("Imię",#selector(focusFirst),"i"),("Zapisz zamówienie",#selector(save),"s"),("Pokaż komunikat",#selector(dialog),"k")] {let x=NSMenuItem(title:name,action:action,keyEquivalent:key);x.target=self;sub.addItem(x)}
  item.submenu=sub;menu.addItem(item);NSApp.mainMenu=menu
  window.makeKeyAndOrderFront(nil);window.makeFirstResponder(first);NSApp.activate(ignoringOtherApps:true)
 }
 @objc func focusFirst(){window.makeFirstResponder(first)}
 @objc func selectRadio(_ b:NSButton){for r in radios {r.state=r==b ? .on:.off}}
 @objc func save(){window.title="UXPomiar zapisano"}
 @objc func cancel(){NSApp.terminate(nil)}
 @objc func dialog(){let a=NSAlert();a.messageText="Potwierdzenie";a.informativeText="Czy na pewno wysłać zamówienie do realizacji?";a.addButton(withTitle:"Tak");a.addButton(withTitle:"Nie");a.runModal()}
 @objc func file(){let p=NSSavePanel();p.nameFieldStringValue="zamowienie.txt";p.runModal()}
}
extension App:NSTableViewDataSource,NSTableViewDelegate {
 func numberOfRows(in tableView:NSTableView)->Int {8}
 func tableView(_ t:NSTableView,objectValueFor column:NSTableColumn?,row:Int)->Any? {"Zamówienie \(row+1)"}
}
let app=NSApplication.shared
let delegate=App();app.delegate=delegate;app.setActivationPolicy(.regular);app.run()
