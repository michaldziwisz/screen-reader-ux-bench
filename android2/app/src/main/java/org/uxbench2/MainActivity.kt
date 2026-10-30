package org.uxbench2
import android.app.Activity
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.*
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.*
import android.util.Log
import androidx.recyclerview.widget.RecyclerView
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.snackbar.Snackbar
import org.json.*

class MainActivity:Activity() {
 companion object { var instance:MainActivity?=null }
 lateinit var root:LinearLayout;lateinit var search:EditText;lateinit var details:EditText;lateinit var status:TextView;lateinit var tts:TextToSpeech
 var selectedRow=-1;var selectedFolder="";var variant="NAZWA";var presentation="RECYCLER"
 lateinit var records:JSONArray;val cols get()=if(variant=="STAN") listOf("Stan","Rozmiar","Data","Nazwa") else listOf("Nazwa","Data","Rozmiar","Stan")
 data class Folder(val number:Int,val name:String,val children:List<Folder> = emptyList(),var expanded:Boolean=false)
 val folders=listOf(Folder(0,"Dokumenty",listOf(Folder(1,"Umowy",listOf(Folder(2,"Najem"),Folder(3,"Praca"))),Folder(4,"Faktury",listOf(Folder(5,"2025"),Folder(6,"2026"),Folder(7,"Korekty"))),Folder(8,"Raporty"))),Folder(9,"Zdjęcia",listOf(Folder(10,"Wakacje"),Folder(11,"Rodzina"))),Folder(12,"Muzyka"))
 val visible= mutableListOf<Pair<Folder,Int>>()
 lateinit var tree:RecyclerView;lateinit var treeAdapter:TreeAdapter
 fun log(kind:String,data:Any) {Log.i("UX_APP",JSONObject().put("time_ms",System.currentTimeMillis()).put("kind",kind).put("data",data).toString())}
 fun identify(v:View,name:String) {v.id=resources.getIdentifier(name,"id",packageName);v.setOnFocusChangeListener {_,yes->if(yes)log("focus",name)}}
 fun text(s:String)=TextView(this).apply {text=s;textSize=16f}
 fun section(name:String):LinearLayout {val g=LinearLayout(this);g.orientation=1;g.accessibilityPaneTitle=name;g.importantForAccessibility=View.IMPORTANT_FOR_ACCESSIBILITY_YES;val title=text(name);title.isAccessibilityHeading=true;g.addView(title);root.addView(g);return g}
 override fun onCreate(b:Bundle?) {
  super.onCreate(b);instance=this;variant=intent.getStringExtra("variant")?:"NAZWA";presentation=intent.getStringExtra("presentation")?:"RECYCLER"
  val f=JSONObject(assets.open("fixture.json").bufferedReader().readText());records=f.getJSONArray("records")
  val scroll=ScrollView(this);root=LinearLayout(this);root.orientation=1;root.setPadding(12,12,12,12);scroll.addView(root);setContentView(scroll)
  val tools=section("Narzędzia");val bar=LinearLayout(this)
  for((i,name) in listOf("Nowy","Otwórz","Zapisz","Usuń","Kopiuj","Wklej").withIndex())bar.addView(Button(this).apply {text=name;identify(this,"button_$i")},LinearLayout.LayoutParams(0,48,1f))
  tools.addView(bar);search=EditText(this);search.hint="Szukaj";search.contentDescription="Szukaj";search.isSingleLine=true;identify(search,"search");tools.addView(search)
  val fg=section("Foldery");tree=RecyclerView(this);tree.layoutManager=LinearLayoutManager(this);identify(tree,"folders");treeAdapter=TreeAdapter();tree.adapter=treeAdapter;tree.isNestedScrollingEnabled=false;fg.addView(tree,LinearLayout.LayoutParams(-1,240));rebuildTree()
  val pg=section("Pliki")
  if(presentation=="TABLE") {
   val grid=TableLayout(this);identify(grid,"files")
   val header=TableRow(this);cols.forEach{header.addView(text(it).apply {isAccessibilityHeading=true},TableRow.LayoutParams(0,32,1f))};grid.addView(header)
   for(i in 0 until records.length()){val row=TableRow(this);for((j,col) in cols.withIndex()){val t=text(records.getJSONObject(i).getString(col));t.isFocusable=true;identify(t,"cell_${i}_${j}");t.setOnClickListener {selectedRow=i;log("selectedRow",i)};row.addView(t,TableRow.LayoutParams(0,32,1f))};grid.addView(row)}
   pg.addView(grid)
  }else {
   val rv=RecyclerView(this);rv.layoutManager=LinearLayoutManager(this);rv.isNestedScrollingEnabled=false;identify(rv,"files");rv.adapter=FileAdapter();pg.addView(rv,LinearLayout.LayoutParams(-1,640))
  }
  pg.addView(Button(this).apply {text="Dalej";identify(this,"after_files")})
  val dg=section("Szczegóły");details=EditText(this);details.setText(f.getString("details"));details.inputType=android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE;details.keyListener=null;details.setTextIsSelectable(true);details.contentDescription="Szczegóły";identify(details,"details");dg.addView(details)
  status=text("Gotowe");identify(status,"status");root.addView(status)
  tts=TextToSpeech(this,{},packageName);search.requestFocus();log("ready",JSONObject().put("variant",variant).put("presentation",presentation).put("records",records.length()))
 }
 override fun onDestroy(){if(instance===this)instance=null;tts.shutdown();super.onDestroy()}
 fun probe(){tts.speak("Kontrola kanału mowy",TextToSpeech.QUEUE_FLUSH,null,"positive")}
 fun anchor(target:String){
   val id=resources.getIdentifier(target,"id",packageName)
   val focus={log("anchor",JSONObject().put("target",target).put("accepted",findViewById<View>(id)?.requestFocus()?:false))}
   if(target.startsWith("row_")){
    val rv=findViewById<RecyclerView>(resources.getIdentifier("files","id",packageName))
    rv.scrollToPosition(target.removePrefix("row_").toInt());rv.postDelayed({focus()},250)
   }else focus()
  }
 fun emit(mode:String,count:Int) {
  status.accessibilityLiveRegion=when(mode){"polite"->View.ACCESSIBILITY_LIVE_REGION_POLITE;"assertive"->View.ACCESSIBILITY_LIVE_REGION_ASSERTIVE;else->View.ACCESSIBILITY_LIVE_REGION_NONE}
  for(i in 1..count){val s=if(count==1)"Kontrola komunikatu $mode" else "Plik $i z 5 skopiowany";log("emit",JSONObject().put("mode",mode).put("text",s));when(mode){"toast"->Toast.makeText(this,s,Toast.LENGTH_SHORT).show();"snackbar"->Snackbar.make(root,s,Snackbar.LENGTH_SHORT).show();else->status.text=s}}
 }
 fun state(){log("state",JSONObject().put("selectedRow",selectedRow).put("selectedFolder",selectedFolder).put("detailsSelectionStart",details.selectionStart).put("detailsSelectionEnd",details.selectionEnd).put("focusId",currentFocus?.let{runCatching{resources.getResourceEntryName(it.id)}.getOrDefault("unknown") }?:""))}
 fun rebuildTree(){visible.clear();fun visit(nodes:List<Folder>,depth:Int){for(n in nodes){visible.add(n to depth);if(n.expanded)visit(n.children,depth+1)}};visit(folders,0);treeAdapter.notifyDataSetChanged()}
 inner class Holder(val t:TextView):RecyclerView.ViewHolder(t)
 inner class FileAdapter:RecyclerView.Adapter<Holder>() {
  override fun getItemCount()=records.length()
  override fun onCreateViewHolder(p:ViewGroup,v:Int)=Holder(text("").apply {layoutParams=RecyclerView.LayoutParams(-1,32);isFocusable=true})
  override fun onBindViewHolder(h:Holder,i:Int){val record=records.getJSONObject(i);h.t.text=cols.joinToString("; "){col->"$col: ${record.getString(col)}"};identify(h.t,"row_$i");h.t.setOnClickListener {selectedRow=i;log("selectedRow",i)}}
 }
 inner class TreeAdapter:RecyclerView.Adapter<Holder>() {
  override fun getItemCount()=visible.size
  override fun onCreateViewHolder(p:ViewGroup,v:Int)=Holder(text("").apply{layoutParams=RecyclerView.LayoutParams(-1,32);isFocusable=true})
  override fun onBindViewHolder(h:Holder,i:Int){val(n,depth)=visible[i];h.t.text=n.name;h.t.setPadding(depth*24,0,0,0);identify(h.t,"folder_${n.number}");h.t.stateDescription=if(n.children.isEmpty())null else if(n.expanded)"rozwinięte" else "zwinięte"
   h.t.setOnClickListener {selectedFolder=n.name;if(n.children.isNotEmpty()){n.expanded = !n.expanded;rebuildTree()};log("folder",JSONObject().put("name",n.name).put("level",depth).put("expanded",n.expanded))}
   h.t.accessibilityDelegate=object:View.AccessibilityDelegate(){override fun onInitializeAccessibilityNodeInfo(v:View,info:AccessibilityNodeInfo){super.onInitializeAccessibilityNodeInfo(v,info);info.collectionItemInfo=AccessibilityNodeInfo.CollectionItemInfo.obtain(i,1,0,1,false);if(n.children.isNotEmpty())info.addAction(if(n.expanded)AccessibilityNodeInfo.AccessibilityAction.ACTION_COLLAPSE else AccessibilityNodeInfo.AccessibilityAction.ACTION_EXPAND)};override fun performAccessibilityAction(v:View,action:Int,args:Bundle?):Boolean{if(action==AccessibilityNodeInfo.ACTION_EXPAND||action==AccessibilityNodeInfo.ACTION_COLLAPSE){v.performClick();return true};return super.performAccessibilityAction(v,action,args)}}
  }
 }
}
