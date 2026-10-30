package org.uxbench2
import android.speech.tts.*
import android.util.Log
import android.media.AudioFormat
import org.json.JSONObject

class LogTts: TextToSpeechService() {
 override fun onIsLanguageAvailable(l:String?,c:String?,v:String?) = if(l in listOf("pol","eng","pl","en")) TextToSpeech.LANG_COUNTRY_AVAILABLE else TextToSpeech.LANG_NOT_SUPPORTED
 override fun onGetLanguage() = arrayOf("pol","POL","")
 override fun onLoadLanguage(l:String?,c:String?,v:String?) = TextToSpeech.LANG_COUNTRY_VAR_AVAILABLE
 override fun onStop() {}
 override fun onSynthesizeText(r:SynthesisRequest, c:SynthesisCallback) {
  Log.i("UX_TTS", JSONObject().put("time_ms",System.currentTimeMillis()).put("elapsed_ms",android.os.SystemClock.elapsedRealtime()).put("text",r.charSequenceText.toString()).put("language",r.language).toString())
  c.start(16000,AudioFormat.ENCODING_PCM_16BIT,1)
  val silence=ByteArray(3200)
  c.audioAvailable(silence,0,silence.size); c.done()
 }
}
