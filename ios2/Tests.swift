import XCTest
final class BenchTests:XCTestCase {
 @MainActor func tree(_ s:any XCUIElementSnapshot)->[String:Any] {["id":s.identifier,"label":s.label,"value":s.value.map{String(describing:$0)} ?? "","role":s.elementType.rawValue,"enabled":s.isEnabled,"selected":s.isSelected,"frame":[s.frame.minX,s.frame.minY,s.frame.width,s.frame.height],"children":s.children.map{tree($0)}]}
 func attach(_ name:String,_ value:Any) throws{let d=try JSONSerialization.data(withJSONObject:value,options:[.prettyPrinted,.sortedKeys]);let a=XCTAttachment(data:d,uniformTypeIdentifier:"public.json");a.name=name;a.lifetime = .keepAlways;add(a)}
 @MainActor func testMainWindow() throws {
  continueAfterFailure=false
  for variant in ["NAZWA","STAN"]{
   let app=XCUIApplication();app.launchArguments=[variant,"--fixture-bundle","-AppleLanguages","(pl)","-AppleLocale","pl_PL"];app.launch()
   XCTAssertTrue(app.textFields["search"].waitForExistence(timeout:15))
   var r:[String:Any]=["variant":variant,"evidence":"accessibility_tree","reader":"VoiceOver unavailable in Simulator","initial":tree(try app.snapshot())]
   try attach(variant+"-initial",r)
   app.cells["folder_0"].tap();r["expanded_Dokumenty"]=tree(try app.snapshot())
   app.cells["folder_1"].tap();r["expanded_Umowy"]=tree(try app.snapshot())
   app.cells["folder_2"].tap();r["selected_Najem"]=tree(try app.snapshot())
   app.cells["row_1"].tap();r["selected_file"]=tree(try app.snapshot())
   app.buttons["plain"].tap();r["plain_after"]=tree(try app.snapshot())
   app.buttons["announcement"].tap();r["announcement_after"]=tree(try app.snapshot())
   var bursts:[[String:Any]]=[]
   for i in 1...6{app.buttons["burst"].tap();bursts.append(["repeat":i,"tree":tree(try app.snapshot())])};r["bursts"]=bursts
   app.buttons["export"].tap()
   let shot=XCTAttachment(screenshot:app.screenshot());shot.name=variant;shot.lifetime = .keepAlways;add(shot)
   let list=app.collectionViews["files"];list.swipeUp();r["files_scrolled"]=tree(try app.snapshot())
   try attach(variant+".json",r);app.terminate()
  }
 }
}
