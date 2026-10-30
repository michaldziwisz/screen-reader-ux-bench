package org.uxbench
import android.app.*
import android.os.Bundle
import android.content.Intent
import android.view.View
import android.view.KeyEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.*
import android.speech.tts.TextToSpeech

class MainActivity:Activity() {
 companion object { var instance:MainActivity?=null }
 private var tts:TextToSpeech?=null
 private var fields=mutableMapOf<String,View>()
 override fun onCreate(b:Bundle?) {
  super.onCreate(b); instance=this
  val grouped=intent.getStringExtra("variant")!="PLASKI"
  title="UXPomiar "+if(grouped) "GRUPY" else "PLASKI"
  val outer=LinearLayout(this).apply {orientation=LinearLayout.VERTICAL;setPadding(16,32,16,32)}
  fun label(v:View,id:String,name:String):View {v.contentDescription=name; v.tag=id; v.id=View.generateViewId(); fields[id]=v; return v}
  fun edit(id:String,name:String,value:String=""):View = label(EditText(this).apply {isSingleLine=true;hint=name;setText(value);minimumHeight=48},id,name)
  fun button(id:String,name:String,action:()->Unit):View = label(Button(this).apply {text=name;setOnClickListener { action() }},id,name)
  fields["imie"]=edit("imie","Imię"); fields["nazw"]=edit("nazw","Nazwisko")
  val radio=RadioGroup(this).apply {orientation=LinearLayout.HORIZONTAL;contentDescription="Sposób dostawy"}
  listOf("Kurier","Paczkomat","Odbiór osobisty").forEachIndexed {i,s -> radio.addView(RadioButton(this).apply {text=s;id=View.generateViewId();isChecked=i==0;contentDescription=s}) }
  fields["sposob"]=radio
  fields["kraj"]=label(Spinner(this).apply {adapter=ArrayAdapter(this@MainActivity,android.R.layout.simple_spinner_dropdown_item,listOf("Polska","Czechy","Niemcy","Słowacja"));minimumHeight=48},"kraj","Kraj")
  fields["szt"]=edit("szt","Liczba sztuk","1").apply {(this as EditText).inputType=2}
  fields["faktura"]=label(CheckBox(this).apply {text="Wystaw fakturę"},"faktura","Wystaw fakturę")
  fields["news"]=label(CheckBox(this).apply {text="Zapisz na newsletter"},"news","Zapisz na newsletter")
  fields["lista"]=ListView(this).apply {
   contentDescription="Ostatnie zamówienia"
   adapter=ArrayAdapter(this@MainActivity,android.R.layout.simple_list_item_single_choice,(1..8).map {"Zamówienie $it"})
   choiceMode=ListView.CHOICE_MODE_SINGLE
   layoutParams=LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,384)
  }
  fields["zapisz"]=button("zapisz","Zapisz zamówienie") {title="Zapisano zamówienie";outer.announceForAccessibility("Zapisano zamówienie")}
  fields["anuluj"]=button("anuluj","Anuluj") {finish()}
  fields["komunikat"]=button("komunikat","Pokaż komunikat") {dialog()}
  fields["plik"]=button("plik","Zapisz jako plik") {startActivity(Intent(Intent.ACTION_CREATE_DOCUMENT).apply {type="text/plain";addCategory(Intent.CATEGORY_OPENABLE);putExtra(Intent.EXTRA_TITLE,"zamowienie.txt")})}
  fun add(parent:LinearLayout, ids:List<String>) {ids.forEach {parent.addView(fields[it])}}
  if(grouped) {
   listOf("Dane odbiorcy" to listOf("imie","nazw"),"Dostawa" to listOf("sposob","kraj","szt"),"Opcje" to listOf("faktura","news","lista")).forEach {(name,ids)->
    val group=LinearLayout(this).apply {orientation=LinearLayout.VERTICAL;contentDescription=name;isFocusable=false}
    outer.addView(group);add(group,ids)
   }
   add(outer,listOf("zapisz","anuluj","komunikat","plik"))
  } else add(outer,listOf("zapisz","lista","nazw","news","szt","komunikat","imie","sposob","anuluj","kraj","faktura","plik"))
  setContentView(ScrollView(this).apply {addView(outer)})
  fields["imie"]?.requestFocus()
 }
 fun dialog() {AlertDialog.Builder(this).setTitle("Potwierdzenie").setMessage("Czy na pewno wysłać zamówienie do realizacji?").setPositiveButton("Tak") {d,_->d.dismiss()}.setNegativeButton("Nie") {d,_->d.dismiss()}.show()}
 fun probe() {android.util.Log.i("UX_AX","PROBE_REQUEST");tts=TextToSpeech(this,{status-> android.util.Log.i("UX_AX","TTS_INIT $status");if(status==TextToSpeech.SUCCESS) tts?.speak("Kontrola kanału mowy",TextToSpeech.QUEUE_FLUSH,null,"probe")},"org.uxbench")}
 override fun onKeyShortcut(keyCode:Int,event:KeyEvent):Boolean {
  if(event.isCtrlPressed && keyCode==KeyEvent.KEYCODE_S) {fields["zapisz"]?.performClick();return true}
  return super.onKeyShortcut(keyCode,event)
 }
}
