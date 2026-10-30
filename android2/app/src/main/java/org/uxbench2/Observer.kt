package org.uxbench2
import android.accessibilityservice.*
import android.view.accessibility.*
import android.content.*
import android.graphics.Path
import android.util.Log
import android.os.Bundle
import org.json.*

class Observer:AccessibilityService() {
 companion object {var instance:Observer?=null}
 override fun onServiceConnected(){instance=this;Log.i("UX_AX","OBSERVER_READY")}
 override fun onInterrupt(){}
 fun node(n:AccessibilityNodeInfo):JSONObject {
  val r=JSONObject().put("id",n.viewIdResourceName?:"").put("label",n.contentDescription?.toString()?:"").put("text",n.text?.toString()?:"").put("role",n.className?.toString()?:"").put("heading",n.isHeading).put("pane",n.paneTitle?.toString()?:"").put("state",n.stateDescription?.toString()?:"").put("focused",n.isFocused).put("a11yFocused",n.isAccessibilityFocused).put("selected",n.isSelected).put("visible",n.isVisibleToUser).put("editable",n.isEditable).put("actions",JSONArray(n.actionList.map{it.id}))
  n.collectionInfo?.let{r.put("collection",JSONObject().put("rows",it.rowCount).put("columns",it.columnCount).put("hierarchical",it.isHierarchical))}
  n.collectionItemInfo?.let{r.put("item",JSONObject().put("row",it.rowIndex).put("column",it.columnIndex))};return r
 }
 override fun onAccessibilityEvent(e:AccessibilityEvent){if(e.packageName?.toString()!="org.uxbench2")return
  val r=JSONObject().put("time_ms",System.currentTimeMillis()).put("event",e.eventType).put("contentChangeTypes",e.contentChangeTypes).put("text",e.text.joinToString(" "));e.source?.let{r.put("node",node(it))};Log.i("UX_AX",r.toString())
 }
 fun snapshot(){fun visit(n:AccessibilityNodeInfo,path:String){Log.i("UX_TREE",node(n).put("path",path).toString());for(i in 0 until n.childCount)n.getChild(i)?.let{visit(it,"$path/$i")}};rootInActiveWindow?.takeIf{it.packageName=="org.uxbench2"}?.let{visit(it,"0")}}
 fun action(target:String,action:Int,granularity:Int=0){fun visit(n:AccessibilityNodeInfo):Boolean{if(n.viewIdResourceName=="org.uxbench2:id/$target"){val args=Bundle();if(granularity>0){args.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_MOVEMENT_GRANULARITY_INT,granularity);args.putBoolean(AccessibilityNodeInfo.ACTION_ARGUMENT_EXTEND_SELECTION_BOOLEAN,false)};val ok=n.performAction(action,args);Log.i("UX_ACTION",JSONObject().put("target",target).put("action",action).put("ok",ok).toString());return true};for(i in 0 until n.childCount)if(n.getChild(i)?.let{visit(it)}==true)return true;return false};rootInActiveWindow?.let{visit(it)}}
 fun gesture(direction:String){val root=rootInActiveWindow?:return;if(root.packageName!="org.uxbench2")return;val rect=android.graphics.Rect();root.getBoundsInScreen(rect);val x=rect.centerX().toFloat();val y=rect.centerY().toFloat();val dx=rect.width()*0.25f;val dy=rect.height()*0.2f;val path=Path();when(direction){"up"->{path.moveTo(x,y+dy);path.lineTo(x,y-dy)};"down"->{path.moveTo(x,y-dy);path.lineTo(x,y+dy)};else->{path.moveTo(x-dx,y);path.lineTo(x+dx,y)}}
  val ok=dispatchGesture(GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(path,0,220)).build(),object:GestureResultCallback(){override fun onCompleted(g:GestureDescription){Log.i("UX_ACTION","gesture completed $direction")};override fun onCancelled(g:GestureDescription){Log.i("UX_ACTION","gesture cancelled $direction")}},null);Log.i("UX_ACTION","gesture accepted $ok $direction")
 }
}
class Control:BroadcastReceiver(){override fun onReceive(c:Context,i:Intent){val cmd=i.getStringExtra("command")?:"";Log.i("UX_ACTION","CONTROL $cmd activity=${MainActivity.instance!=null} observer=${Observer.instance!=null}");when(cmd){
 "tree"->Observer.instance?.snapshot();"action"->Observer.instance?.action(i.getStringExtra("target")?:"search",i.getIntExtra("action",64),i.getIntExtra("granularity",0));"gesture"->Observer.instance?.gesture(i.getStringExtra("direction")?:"right");"anchor"->MainActivity.instance?.anchor(i.getStringExtra("target")?:"search");"probe"->MainActivity.instance?.probe();"state"->MainActivity.instance?.state();"emit"->MainActivity.instance?.emit(i.getStringExtra("mode")?:"plain",i.getIntExtra("count",1))
}}}
