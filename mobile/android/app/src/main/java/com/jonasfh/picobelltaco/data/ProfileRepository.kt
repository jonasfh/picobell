package com.jonasfh.picobelltaco.data

import android.content.Context
import androidx.preference.PreferenceManager
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Callback
import com.google.gson.Gson
import okhttp3.Call
import okhttp3.Response
import java.io.IOException


class ProfileRepository(private val context: Context) {
    private val prefs = PreferenceManager.getDefaultSharedPreferences(context)
    private val client = OkHttpClient()

    fun getProfile(callback: (ProfileResponse?) -> Unit) {
        val token = prefs.getString("access_token", null) ?: return callback(null)
        val request = Request.Builder()
            .url("https://picobell.no/profile")
            .addHeader("Authorization", "Bearer $token")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) = callback(null)
            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let {
                    val profile = Gson().fromJson(it, ProfileResponse::class.java)
                    callback(profile)
                } ?: callback(null)
            }
        })
    }
}

data class ProfileResponse(
    val user: String,
    val apartments: List<String>,
    val devices: List<String>
)
