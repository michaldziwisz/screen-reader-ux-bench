plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
 namespace = "org.uxbench2"
 compileSdk = 35
 defaultConfig { applicationId = "org.uxbench2"; minSdk = 30; targetSdk = 35; versionCode = 1; versionName = "2.0" }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
 kotlinOptions { jvmTarget = "17" }
 sourceSets["main"].assets.srcDir("../../shared2")
}

dependencies { implementation("androidx.recyclerview:recyclerview:1.4.0"); implementation("com.google.android.material:material:1.12.0"); implementation("androidx.test.uiautomator:uiautomator:2.3.0") }
