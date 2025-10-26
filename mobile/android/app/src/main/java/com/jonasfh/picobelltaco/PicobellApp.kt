package com.jonasfh.picobelltaco

import android.app.Application
import androidx.emoji.text.EmojiCompat
import androidx.emoji.bundled.BundledEmojiCompatConfig
import com.google.firebase.FirebaseApp


class PicobellApp : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)
        val config = BundledEmojiCompatConfig(this)
        EmojiCompat.init(config)
    }
}
