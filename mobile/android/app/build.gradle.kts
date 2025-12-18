plugins {
    id("com.android.application")
    kotlin("android")
    id("com.google.gms.google-services")
}

android {
    namespace = "com.jonasfh.picobelltaco"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.jonasfh.picobelltaco"
        minSdk = 26
        targetSdk = 34
        versionCode = 7
        versionName = "1.0.5"
        buildConfigField("String", "SERVER_URL", "\"https://picobell.no\"")
        buildConfigField("String", "OAUTH2_CLIENT_ID", "\"1032602808859-892rqn0vi2i963d1n65d3kpsimi37nrk.apps.googleusercontent.com\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.9.0")
    implementation("androidx.emoji:emoji-bundled:1.1.0")

    // Firebase BOM determines the messaging (and possibly other Firebase libraries) version
    implementation(platform("com.google.firebase:firebase-bom:34.6.0"))
    implementation("com.google.firebase:firebase-messaging")

    // Analytics not working
    // implementation("com.google.firebase:firebase-analytics")

    // Google / HTTP / Coroutines
    implementation("com.google.android.gms:play-services-auth:21.4.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
    // --- TESTING ---
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
    // Retrofit
    // implementation("com.squareup.retrofit2:retrofit:3.0.0")
    implementation("com.squareup.retrofit2:converter-gson:3.0.0")
    // implementation("com.squareup.okhttp3:logging-interceptor:5.2.1")
    // Security
     implementation("androidx.preference:preference-ktx:1.2.1")
}
