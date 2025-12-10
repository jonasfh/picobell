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
import java.lang.Exception

data class ApartmentCreateResponse(
    val id: Int,
    val api_key: String
)

class ApartmentRepository(private val context: Context) {

    private val tokenManager = TokenManager(context)
    private val client = HttpClientProvider.getInstance(context)
    private val gson = Gson()

    /**
     * Returnerer api_key fra server,
     * eller null hvis noe feilet.
     */
    suspend fun createApartment(
        address: String,
        picoSerial: String
    ): String? = withContext(Dispatchers.IO) {

        val bodyJson = gson.toJson(
            mapOf(
                "address" to address,
                "pico_serial" to picoSerial
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
                    Log.e("APT", "Feil: ${resp.code}")
                    val errorText = resp.body?.string()
                    Log.e("APT", "Body: $errorText")
                    return@withContext null
                }

                val json = resp.body?.string()
                Log.d("APT", "Respons: $json")

                val parsed = gson.fromJson(
                    json,
                    ApartmentCreateResponse::class.java
                )

                parsed.api_key
            }
        } catch (e: Exception) {
            Log.e("APT", "Exception", e)
            null
        }
    }
    suspend fun deleteApartment(id: Int): Boolean = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("https://picobell.no/profile/apartments/$id")
            .delete()
            .build()

        try {
            client.newCall(request).execute().use { resp ->
                resp.isSuccessful
            }
        } catch (e: Exception) {
            Log.e("APT", "Exception", e)
            false
        }
    }

    suspend fun changeApartmentAddress(id: Int, address: String): Boolean = withContext(Dispatchers.IO) {
        val bodyJson = gson.toJson(
            mapOf(
                "address" to address
            )
        )

        val media = "application/json".toMediaType()
        val requestBody = bodyJson.toRequestBody(media)
        val request = Request.Builder()
            .url("https://picobell.no/profile/apartments/$id")
            .put(requestBody)
            .build()

        try {
            client.newCall(request).execute().use { resp ->
                resp.isSuccessful
            }
        } catch (e: Exception) {
            Log.e("APT", "Exception", e)
            false
        }
    }

    suspend fun openApartmentDoor(id: Int): Boolean = withContext(Dispatchers.IO) {
        val requestBody = "".toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url("https://picobell.no/profile/apartments/$id/open")
            .post(requestBody)
            .build()

        try {
            client.newCall(request).execute().use { resp ->
                if (!resp.isSuccessful) {
                    Log.e("APT", "Feil: ${resp.code}")
                    val errorText = resp.body?.string()
                    Log.e("APT", "Body: $errorText")
                    false
                }
                val json = resp.body?.string()
                Log.d("APT", "Respons: $json")
                true
            }
        } catch (e: Exception) {
            Log.e("APT", "Exception", e)
            false
        }
    }
}
