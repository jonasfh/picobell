package com.jonasfh.picobelltaco.data

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.jonasfh.picobelltaco.auth.HttpClientProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class DeviceRepository(private val context: Context) {
    private val client = HttpClientProvider.getInstance(context)
    private val gson = Gson()

    suspend fun registerDevice(fcmToken: String): Boolean =
        withContext(Dispatchers.IO) {
            val body = JSONObject()
                .put("device_token", fcmToken)
                .put(
                    "device_name",
                    "${android.os.Build.MANUFACTURER} - ${android.os.Build.MODEL}"
                ).toString()
                .toRequestBody("application/json".toMediaType())
            Log.d("DEVICE", "Register device: ")

            val request = Request.Builder()
                .url("https://picobell.no/devices/register")
                .post(body)
                .build()

            try {
                client.newCall(request).execute().use { response ->
                    Log.d("DEVICE", "Register response: ${response.code}")
                    response.isSuccessful
                }
            } catch (e: Exception) {
                Log.e("DEVICE", "Failed to register device", e)
                false
            }
        }

    suspend fun deleteDevice(deviceId: Int): Boolean =
        withContext(Dispatchers.IO) {
            val request = Request.Builder()
                .url("https://picobell.no/devices/$deviceId")
                .delete()
                .build()

            try {
                client.newCall(request).execute().use { response ->
                    Log.d("DEVICE", "Delete response: ${response.code}")
                    response.isSuccessful
                }
            } catch (e: Exception) {
                Log.e("DEVICE", "Failed to delete device", e)
                false
            }
        }
}
