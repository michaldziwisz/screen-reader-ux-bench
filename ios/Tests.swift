import XCTest

final class BenchTests:XCTestCase {
 @MainActor
 func tree(_ s:any XCUIElementSnapshot)->[String:Any] {
  ["id":s.identifier,"label":s.label,"value":s.value.map {String(describing:$0)} ?? "","role":s.elementType.rawValue,"enabled":s.isEnabled,"selected":s.isSelected,"frame":[s.frame.minX,s.frame.minY,s.frame.width,s.frame.height],"children":s.children.map{tree($0)}]
 }
 func attach(_ name:String,_ object:Any) throws {
  let data=try JSONSerialization.data(withJSONObject:object,options:[.prettyPrinted,.sortedKeys])
  let a=XCTAttachment(data:data,uniformTypeIdentifier:"public.json");a.name=name;a.lifetime = .keepAlways;add(a)
 }
 @MainActor
 func testForms() throws {
  continueAfterFailure=false
  for variant in ["GRUPY","PLASKI"] {
   let app=XCUIApplication();app.launchArguments=[variant,"-AppleLanguages","(pl)","-AppleLocale","pl_PL"];app.launch()
   XCTAssertTrue(app.textFields["imie"].waitForExistence(timeout:10))
   var result:[String:Any]=["variant":variant,"evidence":"accessibility_tree","reader":"VoiceOver unavailable in Simulator","tree":tree(try app.snapshot()),"debug":app.debugDescription]
   let shot=XCTAttachment(screenshot:app.screenshot());shot.name=variant;shot.lifetime = .keepAlways;add(shot)
   var audits:[String]=[]
   do {try app.performAccessibilityAudit {issue in audits.append(issue.debugDescription);return true}}catch {result["audit_error"]=String(describing:error)}
   result["audit_issues"]=audits
   app.buttons["komunikat"].tap()
   XCTAssertTrue(app.alerts.firstMatch.waitForExistence(timeout:3))
   result["dialog_before"]=tree(try app.snapshot())
   app.typeKey(XCUIKeyboardKey.escape,modifierFlags:[])
   result["dialog_after_escape"]=tree(try app.snapshot())
   result["escape_closed_dialog"] = !app.alerts.firstMatch.exists
   if app.alerts.firstMatch.exists {app.alerts.buttons["Nie"].tap()}
   app.typeKey("s",modifierFlags:.command)
   result["after_shortcut"]=tree(try app.snapshot())
   try attach(variant+".json",result)
   app.terminate()
  }
 }
}
