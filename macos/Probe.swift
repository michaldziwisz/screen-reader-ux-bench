import AppKit
import ApplicationServices
let pid=pid_t(CommandLine.arguments[1])!
let app=AXUIElementCreateApplication(pid)
func attr(_ e:AXUIElement,_ a:String)->Any? {var v:CFTypeRef?;if AXUIElementCopyAttributeValue(e,a as CFString,&v) == .success{return v};return nil}
func node(_ e:AXUIElement,_ depth:Int=0)->[String:Any] {
 var r:[String:Any]=[:]
 for a in ["AXRole","AXSubrole","AXTitle","AXDescription","AXValue","AXIdentifier","AXEnabled","AXFocused","AXSelected"] {
  if let v=attr(e,a) {r[a]=String(describing:v)}
 }
 if depth<18, let children=attr(e,"AXChildren") as? [AXUIElement] {r["children"]=children.map{node($0,depth+1)}}
 return r
}
var result:[String:Any]=["pid":pid,"front_pid":NSWorkspace.shared.frontmostApplication?.processIdentifier ?? -1,"front_bundle":NSWorkspace.shared.frontmostApplication?.bundleIdentifier ?? ""]
if let focused=attr(app,"AXFocusedUIElement") {result["focus"]=node(focused as! AXUIElement)}
if CommandLine.arguments.contains("tree") {result["tree"]=node(app)}
print(String(data:try! JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]),encoding:.utf8)!)
