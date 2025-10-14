package com.jonasfh.picobelltaco.auth

import android.content.Context
import okhttp3.OkHttpClient

object HttpClientProvider {

    @Volatile
    private var instance: OkHttpClient? = null

    fun getInstance(context: Context): OkHttpClient {
        return instance ?: synchronized(this) {
            instance ?: OkHttpClient.Builder()
                .addInterceptor(AuthInterceptor(context))
                .build()
                .also { instance = it }
        }
    }
}
