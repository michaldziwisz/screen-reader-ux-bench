package org.uxbench2
import android.app.Instrumentation
import android.app.UiAutomation
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import android.util.Log
import androidx.test.uiautomator.UiDevice

/** Ta próba może restartować proces docelowy. Uruchamiana dopiero po głównym pomiarze. */
class GestureProbe:Instrumentation(){
 override fun onCreate(b:Bundle?){super.onCreate(b);start()}
 override fun onStart(){
  val result=Bundle()
  try {
   getUiAutomation(UiAutomation.FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES)
   val device=UiDevice.getInstance(this)
   startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
   SystemClock.sleep(12000)
   for(k in 0..2){
    targetContext.sendBroadcast(Intent().setComponent(android.content.ComponentName("org.uxbench2","org.uxbench2.Control")).putExtra("command","action").putExtra("target",if(k%2==0)"search" else "row_0").putExtra("action",64));SystemClock.sleep(1800)
    Log.i("UX_ACTION","INSTRUMENT_SWIPE_BEGIN $k")
    val ok=device.swipe(device.displayWidth/4,device.displayHeight/2,device.displayWidth*3/4,device.displayHeight/2,40)
    Log.i("UX_ACTION","INSTRUMENT_SWIPE_END $k $ok");SystemClock.sleep(2000)
   }
   result.putString("result","swipe attempts completed, inspect focus events")
  }catch(e:Throwable){result.putString("error",e.toString())}
  finish(android.app.Activity.RESULT_OK,result)
 }
}
