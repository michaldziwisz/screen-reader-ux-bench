package org.uxbench
import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.content.*
import android.util.Log
import org.json.*

class Observer: AccessibilityService() {
 companion object { var instance:Observer?=null }
 override fun onServiceConnected() { instance=this; Log.i("UX_AX","OBSERVER_READY") }
 override fun onInterrupt() {}
 fun node(n:AccessibilityNodeInfo):JSONObject = JSONObject().put("id",n.viewIdResourceName ?: "").put("label",n.contentDescription?.toString() ?: "").put("text",n.text?.toString() ?: "").put("role",n.className?.toString() ?: "").put("enabled",n.isEnabled).put("checked",n.isChecked).put("checkable",n.isCheckable).put("selected",n.isSelected).put("focusable",n.isFocusable).put("a11yFocused",n.isAccessibilityFocused).put("visible",n.isVisibleToUser)
 override fun onAccessibilityEvent(e:AccessibilityEvent) {
  if(e.packageName?.toString()!="org.uxbench") return
  if(e.eventType==AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUSED || e.eventType==AccessibilityEvent.TYPE_VIEW_FOCUSED || e.eventType==AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
   val data=JSONObject().put("time_ms",System.currentTimeMillis()).put("event",e.eventType).put("event_text",e.text.joinToString(" "))
   e.source?.let {data.put("node",node(it))}; Log.i("UX_AX",data.toString())
  }
 }
 fun snapshot() {
  val root=rootInActiveWindow ?: return
  fun visit(n:AccessibilityNodeInfo, path:String) {
   Log.i("UX_TREE",node(n).put("path",path).toString())
   for(i in 0 until n.childCount) n.getChild(i)?.let {visit(it,"$path/$i")}
  }
  visit(root,"0")
 }
 fun focus(label:String) {
  fun visit(n:AccessibilityNodeInfo):Boolean {
   if(n.contentDescription?.toString()==label) return n.performAction(AccessibilityNodeInfo.ACTION_ACCESSIBILITY_FOCUS)
   for(i in 0 until n.childCount) {if(n.getChild(i)?.let {visit(it)}==true) return true}
   return false
  }
  rootInActiveWindow?.let { visit(it) }
 }
}
class Control:BroadcastReceiver() {
 override fun onReceive(c:Context,i:Intent) {
  Log.i("UX_AX","CONTROL ${i.getStringExtra("command")} activity=${MainActivity.instance!=null} observer=${Observer.instance!=null}")
  when(i.getStringExtra("command")) {
   "tree" -> Observer.instance?.snapshot()
   "focus" -> Observer.instance?.focus(i.getStringExtra("label") ?: "Imię")
   "dialog" -> MainActivity.instance?.dialog()
   "probe" -> MainActivity.instance?.probe()
   "anchor" -> MainActivity.instance?.anchor()
  }
 }
}
