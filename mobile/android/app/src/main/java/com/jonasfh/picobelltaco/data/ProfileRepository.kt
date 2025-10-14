package com.jonasfh.picobelltaco.data

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.jonasfh.picobelltaco.auth.TokenManager
import com.jonasfh.picobelltaco.auth.HttpClientProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Request

class ProfileRepository(private val context: Context) {
    private val tokenManager = TokenManager(context)
    private val client = HttpClientProvider.getInstance(context)
    private val gson = Gson()

    suspend fun getProfile(): ProfileResponse? = withContext(Dispatchers.IO) {
        Log.d("PROFILE", "Getting profile")

        val request = Request.Builder()
            .url("https://picobell.no/profile")
            .build()

        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    Log.e("PROFILE", "Request failed with code ${response.code}")
                    return@withContext null
                }

                val body = response.body?.string() ?: return@withContext null
                Log.d("PROFILE", "Response body: ${body.take(200)}")

                gson.fromJson(body, ProfileResponse::class.java)
            }
        } catch (e: Exception) {
            Log.e("PROFILE", "Error fetching profile", e)
            null
        }
    }
}

data class ProfileResponse(
    val id: Int,
    val email: String,
    val role: String,
    val created_at: String,
    val modified_at: String,
    val apartments: List<Apartment>,
    val devices: List<Device>
)

data class Apartment(
    val id: Int,
    val address: String,
    val created_at: String,
    val modified_at: String
)

data class Device(
    val id: Int,
    val name: String,
    val created_at: String,
    val modified_at: String
)
