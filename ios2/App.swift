import UIKit

@main final class AppDelegate:UIResponder,UIApplicationDelegate {
 var window:UIWindow?
 func application(_ a:UIApplication,didFinishLaunchingWithOptions o:[UIApplication.LaunchOptionsKey:Any]?=nil)->Bool {window=UIWindow(frame:UIScreen.main.bounds);window?.rootViewController=BenchController();window?.makeKeyAndVisible();return true}
}
final class BenchController:UIViewController,UICollectionViewDelegate {
 let variant=ProcessInfo.processInfo.arguments.contains("STAN") ? "STAN":"NAZWA"
 var cols:[String]{variant=="STAN" ? ["Stan","Rozmiar","Data","Nazwa"] : ["Nazwa","Data","Rozmiar","Stan"]}
 let names=["Dokumenty","Umowy","Najem","Praca","Faktury","2025","2026","Korekty","Raporty","Zdjęcia","Wakacje","Rodzina","Muzyka"]
 let folderChildren=[0:[1,4,8],1:[2,3],4:[5,6,7],9:[10,11]]
 var tree:UICollectionView!;var files:UICollectionView!;var source:UICollectionViewDiffableDataSource<Int,Int>!;var fileSource:UICollectionViewDiffableDataSource<Int,Int>!
 let status=UILabel();var events:[[String:Any]]=[];var fileSelected = -1
 func identify(_ v:UIView,_ id:String,_ label:String?=nil){v.accessibilityIdentifier=id;if let label=label {v.accessibilityLabel=label}}
 func journal(_ kind:String,_ data:Any){events.append(["kind":kind,"data":data,"time":Date().timeIntervalSince1970]);export()}
 func semantics(_ v:UIView)->[String:Any]{["id":v.accessibilityIdentifier ?? "","label":v.accessibilityLabel ?? "","value":v.accessibilityValue ?? "","isElement":v.isAccessibilityElement,"traits":v.accessibilityTraits.rawValue,"header":v.accessibilityTraits.contains(.header),"containerType":v.accessibilityContainerType.rawValue,"groupChildren":v.shouldGroupAccessibilityChildren,"children":v.subviews.map{semantics($0)}]}
 func export(){let result:[String:Any]=["variant":variant,"evidence":"runtime_app_properties_not_reader","events":events,"fileSelected":fileSelected,"semantics":semantics(view)];let dir=FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0];try? JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:dir.appendingPathComponent("bench2-\(variant).json"),options:.atomic)}
 func button(_ id:String,_ title:String,_ action:@escaping ()->Void)->UIButton{let b=UIButton(type:.system);b.setTitle(title,for:.normal);identify(b,id);b.addAction(UIAction{_ in action()},for:.touchUpInside);return b}
 func group(_ name:String,_ id:String)->UIStackView{let s=UIStackView();s.axis = .vertical;s.spacing=4;s.isAccessibilityElement=false;s.shouldGroupAccessibilityChildren=true;s.accessibilityContainerType = .semanticGroup;identify(s,"group_"+id,name);let label=UILabel();label.text=name;label.accessibilityTraits = .header;identify(label,"heading_"+id);s.addArrangedSubview(label);return s}
 override func viewDidLoad(){
  super.viewDidLoad();view.backgroundColor = .systemBackground
  let root=UIStackView();root.axis = .vertical;root.spacing=10;root.translatesAutoresizingMaskIntoConstraints=false;view.addSubview(root);NSLayoutConstraint.activate([root.topAnchor.constraint(equalTo:view.safeAreaLayoutGuide.topAnchor,constant:12),root.leadingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.leadingAnchor,constant:12),root.trailingAnchor.constraint(equalTo:view.safeAreaLayoutGuide.trailingAnchor,constant:-12)])
  let tools=group("Narzędzia","tools");let bar=UIStackView();bar.axis = .horizontal;bar.distribution = .fillEqually
  for (i,name) in ["Nowy","Otwórz","Zapisz","Usuń","Kopiuj","Wklej"].enumerated(){bar.addArrangedSubview(button("button_\(i)",name,{}))};tools.addArrangedSubview(bar)
  let search=UITextField();search.borderStyle = .roundedRect;search.placeholder="Szukaj";identify(search,"search","Szukaj");tools.addArrangedSubview(search);root.addArrangedSubview(tools)
  let middle=UIStackView();middle.axis = .horizontal;middle.spacing=12;root.addArrangedSubview(middle)
  let fg=group("Foldery","folders");let pg=group("Pliki","files");middle.addArrangedSubview(fg);middle.addArrangedSubview(pg);fg.widthAnchor.constraint(equalToConstant:230).isActive=true
  var config=UICollectionLayoutListConfiguration(appearance:.plain);config.showsSeparators=true
  tree=UICollectionView(frame:.zero,collectionViewLayout:UICollectionViewCompositionalLayout.list(using:config));identify(tree,"folders","Foldery");tree.delegate=self;fg.addArrangedSubview(tree);tree.heightAnchor.constraint(equalToConstant:640).isActive=true
  let registration=UICollectionView.CellRegistration<UICollectionViewListCell,Int>{cell,path,item in var content=cell.defaultContentConfiguration();content.text=self.names[item];content.textProperties.font = .systemFont(ofSize:15);cell.contentConfiguration=content;cell.accessibilityIdentifier="folder_\(item)";cell.accessories=self.folderChildren[item] == nil ? []:[.outlineDisclosure()]}
  source=UICollectionViewDiffableDataSource<Int,Int>(collectionView:tree){v,path,item in v.dequeueConfiguredReusableCell(using:registration,for:path,item:item)}
  var snapshot=NSDiffableDataSourceSectionSnapshot<Int>();snapshot.append([0,9,12]);snapshot.append([1,4,8],to:0);snapshot.append([2,3],to:1);snapshot.append([5,6,7],to:4);snapshot.append([10,11],to:9);source.apply(snapshot,to:0,animatingDifferences:false)
  files=UICollectionView(frame:.zero,collectionViewLayout:UICollectionViewCompositionalLayout.list(using:config));identify(files,"files","Pliki");files.delegate=self;pg.addArrangedSubview(files);files.heightAnchor.constraint(equalToConstant:640).isActive=true
  let fr=UICollectionView.CellRegistration<UICollectionViewListCell,Int>{cell,path,item in var content=cell.defaultContentConfiguration();content.text=self.cols.map{"\($0): \(records[item][$0]!)"}.joined(separator:"; ");content.textProperties.font = .systemFont(ofSize:14);content.textProperties.numberOfLines=2;cell.contentConfiguration=content;cell.accessibilityIdentifier="row_\(item)"}
  fileSource=UICollectionViewDiffableDataSource<Int,Int>(collectionView:files){v,path,item in v.dequeueConfiguredReusableCell(using:fr,for:path,item:item)};var fs=NSDiffableDataSourceSnapshot<Int,Int>();fs.appendSections([0]);fs.appendItems(Array(records.indices));fileSource.apply(fs,animatingDifferences:false)
  let dg=group("Szczegóły","details");let details=UITextView();details.isEditable=false;details.isSelectable=true;details.text=detailsText;details.font = .systemFont(ofSize:16);identify(details,"details","Szczegóły");details.heightAnchor.constraint(equalToConstant:135).isActive=true;dg.addArrangedSubview(details);root.addArrangedSubview(dg)
  status.text="Gotowe";identify(status,"status");root.addArrangedSubview(status)
  let controls=UIStackView();controls.axis = .horizontal;controls.distribution = .fillEqually
  for (id,title,mode,count) in [("plain","Zmień etykietę","plain",1),("announcement","Ogłoś","announcement",1),("burst","Seria","announcement",5)] {controls.addArrangedSubview(button(id,title,{self.emit(mode,count)}))};controls.addArrangedSubview(button("export","Zapisz pomiar",{self.journal("export",true)}));root.addArrangedSubview(controls)
 }
 override func viewDidAppear(_ animated:Bool){super.viewDidAppear(animated);journal("ready",["records":records.count,"voiceOverRunning":UIAccessibility.isVoiceOverRunning])}
 func collectionView(_ v:UICollectionView,didSelectItemAt p:IndexPath){if v===tree,let item=source.itemIdentifier(for:p){var snap=source.snapshot(for:0);if snap.isExpanded(item){snap.collapse([item])}else{snap.expand([item])};source.apply(snap,to:0,animatingDifferences:false);journal("folder",["item":item,"expanded":snap.isExpanded(item)])}else{fileSelected=p.item;journal("fileSelected",p.item)}}
 func emit(_ mode:String,_ count:Int){for i in 1...count {let text=count==1 ? "Kontrola komunikatu \(mode)":"Plik \(i) z 5 skopiowany";status.text=text;if mode=="announcement" {UIAccessibility.post(notification:.announcement,argument:text)};journal("emit",["mode":mode,"text":text,"posted":mode=="announcement","voiceOverRunning":UIAccessibility.isVoiceOverRunning])}}
}
