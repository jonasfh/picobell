package com.jonasfh.picobelltaco.data

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.jonasfh.picobelltaco.auth.HttpClientProvider
import com.jonasfh.picobelltaco.auth.TokenManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody

class ApartmentRepository(private val context: Context) {

    private val tokenManager = TokenManager(context)
    private val client = HttpClientProvider.getInstance(context)
    private val gson = Gson()

    suspend fun createApartment(
        address: String,
        picoSerial: String,
        apiKey: String
    ): Boolean = withContext(Dispatchers.IO) {

        //val token = tokenManager.getToken()
        //if (token == null) {
        //    Log.e("APT", "Ingen token funnet")
        //    return@withContext false
        //}

        val bodyJson = gson.toJson(
            mapOf(
                "address" to address,
                "pico_serial" to picoSerial,
                "api_key" to apiKey
            )
        )

        val media = "application/json".toMediaType()
        val requestBody = bodyJson.toRequestBody(media)

        val request = Request.Builder()
            .url("https://picobell.no/profile/apartments")
            .post(requestBody)
            .build()

        try {
            client.newCall(request).execute().use { resp ->
                if (!resp.isSuccessful) {
                    Log.e("APT", "Feil: HTTP ${resp.code}")
                    Log.e("APT", resp.body?.string() ?: "No body")
                    return@withContext false
                }

                Log.d("APT", "Apartment OK: ${resp.body?.string()}")
                true
            }
        } catch (e: Exception) {
            Log.e("APT", "Exception", e)
            false
        }
    }
}
