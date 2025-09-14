package com.jonasfh.picobelltaco

import android.app.Application
import androidx.emoji.text.EmojiCompat
import androidx.emoji.bundled.BundledEmojiCompatConfig

class PicobellApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val config = BundledEmojiCompatConfig(this)
        EmojiCompat.init(config)
    }
}
