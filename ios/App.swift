import UIKit

@main
final class AppDelegate:UIResponder,UIApplicationDelegate {
 var window:UIWindow?
 func application(_ app:UIApplication,didFinishLaunchingWithOptions options:[UIApplication.LaunchOptionsKey:Any]?=nil)->Bool {
  window=UIWindow(frame:UIScreen.main.bounds);window?.rootViewController=FormController();window?.makeKeyAndVisible();return true
 }
}
final class FormController:UIViewController,UITableViewDataSource,UITableViewDelegate {
 let grouped = !ProcessInfo.processInfo.arguments.contains("PLASKI")
 var first:UITextField!
 var chosen=0
 var buttons:[UIButton]=[]
 override func viewDidLoad() {
  super.viewDidLoad();view.backgroundColor = .systemBackground
  let scroll=UIScrollView();scroll.translatesAutoresizingMaskIntoConstraints=false;view.addSubview(scroll)
  NSLayoutConstraint.activate([scroll.leadingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.leadingAnchor),scroll.trailingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.trailingAnchor),scroll.topAnchor.constraint(equalTo:view.safeAreaLayoutGuide.topAnchor),scroll.bottomAnchor.constraint(equalTo:view.safeAreaLayoutGuide.bottomAnchor)])
  let root=UIStackView();root.axis = .vertical;root.spacing=6;root.translatesAutoresizingMaskIntoConstraints=false;scroll.addSubview(root)
  NSLayoutConstraint.activate([root.leadingAnchor.constraint(equalTo:scroll.contentLayoutGuide.leadingAnchor,constant:16),root.trailingAnchor.constraint(equalTo:scroll.contentLayoutGuide.trailingAnchor,constant:-16),root.topAnchor.constraint(equalTo:scroll.contentLayoutGuide.topAnchor,constant:12),root.bottomAnchor.constraint(equalTo:scroll.contentLayoutGuide.bottomAnchor,constant:-12),root.widthAnchor.constraint(equalTo:scroll.frameLayoutGuide.widthAnchor,constant:-32)])
  var c:[String:UIView]=[:]
  func identify(_ v:UIView,_ id:String,_ label:String) {v.accessibilityIdentifier=id;v.accessibilityLabel=label}
  func edit(_ id:String,_ name:String,_ value:String="")->UIView {
   let f=UITextField();f.borderStyle = .roundedRect;f.placeholder=name;f.text=value;identify(f,id,name);f.heightAnchor.constraint(equalToConstant:44).isActive=true
   if id=="imie" {first=f};if id=="szt" {f.keyboardType = .numberPad};return f
  }
  func button(_ id:String,_ name:String,_ action:Selector)->UIView {
   let b=UIButton(type:.system);b.setTitle(name,for:.normal);identify(b,id,name);b.addTarget(self,action:action,for:.touchUpInside);b.heightAnchor.constraint(equalToConstant:44).isActive=true;return b
  }
  c["imie"]=edit("imie","Imię");c["nazw"]=edit("nazw","Nazwisko");c["szt"]=edit("szt","Liczba sztuk","1")
  let delivery=UIStackView();delivery.axis = .horizontal;delivery.distribution = .fillEqually;delivery.shouldGroupAccessibilityChildren=true;delivery.accessibilityLabel="Sposób dostawy"
  for (i,name) in ["Kurier","Paczkomat","Odbiór osobisty"].enumerated() {let b=UIButton(type:.system);b.setTitle(name,for:.normal);identify(b,"sposob_\(i)",name);b.tag=i;b.accessibilityTraits=i==0 ? [.button,.selected]:.button;b.addTarget(self,action:#selector(selectDelivery(_:)),for:.touchUpInside);buttons.append(b);delivery.addArrangedSubview(b)}
  delivery.heightAnchor.constraint(equalToConstant:44).isActive=true;c["sposob"]=delivery
  let country=UIButton(type:.system);country.setTitle("Kraj: Polska",for:.normal);identify(country,"kraj","Kraj");country.accessibilityValue="Polska";country.showsMenuAsPrimaryAction=true
  country.menu=UIMenu(children:["Polska","Czechy","Niemcy","Słowacja"].map {name in UIAction(title:name) {_ in country.setTitle("Kraj: \(name)",for:.normal);country.accessibilityValue=name}})
  country.heightAnchor.constraint(equalToConstant:44).isActive=true;c["kraj"]=country
  for (id,name) in [("faktura","Wystaw fakturę"),("news","Zapisz na newsletter")] {
   let row=UIStackView();row.axis = .horizontal;let lab=UILabel();lab.text=name;lab.isAccessibilityElement=false;let s=UISwitch();identify(s,id,name);row.addArrangedSubview(lab);row.addArrangedSubview(s);row.heightAnchor.constraint(equalToConstant:44).isActive=true;c[id]=row
  }
  let table=UITableView(frame:.zero,style:.plain);table.dataSource=self;table.delegate=self;table.rowHeight=32;table.isScrollEnabled=false;table.accessibilityIdentifier="lista";table.accessibilityLabel="Ostatnie zamówienia";table.heightAnchor.constraint(equalToConstant:256).isActive=true;c["lista"]=table
  c["zapisz"]=button("zapisz","Zapisz zamówienie",#selector(save));c["anuluj"]=button("anuluj","Anuluj",#selector(cancel));c["komunikat"]=button("komunikat","Pokaż komunikat",#selector(dialog));c["plik"]=button("plik","Zapisz jako plik",#selector(file))
  func add(_ s:UIStackView,_ ids:[String]) {ids.forEach{s.addArrangedSubview(c[$0]!)}}
  if grouped {
   for (name,ids) in [("Dane odbiorcy",["imie","nazw"]),("Dostawa",["sposob","kraj","szt"]),("Opcje",["faktura","news","lista"])] {
    let group=UIStackView();group.axis = .vertical;group.spacing=4;group.isAccessibilityElement=false;group.shouldGroupAccessibilityChildren=true;group.accessibilityContainerType = .semanticGroup;group.accessibilityLabel=name
    let title=UILabel();title.text=name;title.accessibilityTraits = .header;group.addArrangedSubview(title);add(group,ids);root.addArrangedSubview(group)
   }
   add(root,["zapisz","anuluj","komunikat","plik"])
  }else {add(root,["zapisz","lista","nazw","news","szt","komunikat","imie","sposob","anuluj","kraj","faktura","plik"])}
 }
 @objc func selectDelivery(_ b:UIButton){for x in buttons {x.accessibilityTraits=x==b ? [.button,.selected]:.button}}
 @objc func save(){view.accessibilityValue="Zapisano zamówienie";UIAccessibility.post(notification:.announcement,argument:"Zapisano zamówienie")}
 @objc func cancel(){view.endEditing(true)}
 @objc func dialog(){view.endEditing(true);let a=UIAlertController(title:"Potwierdzenie",message:"Czy na pewno wysłać zamówienie do realizacji?",preferredStyle:.alert);a.addAction(UIAlertAction(title:"Tak",style:.default));a.addAction(UIAlertAction(title:"Nie",style:.default));present(a,animated:false)}
 @objc func file(){let url=FileManager.default.temporaryDirectory.appendingPathComponent("zamowienie.txt");try? "Zamówienie testowe".write(to:url,atomically:true,encoding:.utf8);present(UIDocumentPickerViewController(forExporting:[url]),animated:false)}
 override var keyCommands:[UIKeyCommand]? {[UIKeyCommand(title:"Zapisz zamówienie",action:#selector(save),input:"s",modifierFlags:.command)]}
 func tableView(_ t:UITableView,numberOfRowsInSection s:Int)->Int {8}
 func tableView(_ t:UITableView,cellForRowAt path:IndexPath)->UITableViewCell {let cell=UITableViewCell(style:.default,reuseIdentifier:nil);cell.textLabel?.text="Zamówienie \(path.row+1)";cell.accessibilityIdentifier="order_\(path.row+1)";return cell}
}
