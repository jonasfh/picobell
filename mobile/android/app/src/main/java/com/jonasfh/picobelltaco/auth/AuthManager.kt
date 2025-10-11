package com.jonasfh.picobelltaco.auth

import android.content.Context
import android.util.Log
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.jonasfh.picobelltaco.BuildConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class AuthManager(private val context: Context) {

    private val client = OkHttpClient()
    private val tokenManager = TokenManager(context)

    private val gso = GoogleSignInOptions.Builder(
        GoogleSignInOptions.DEFAULT_SIGN_IN
    ).requestIdToken(BuildConfig.OAUTH2_CLIENT_ID)
        .requestEmail()
        .build()

    val signInClient: GoogleSignInClient =
        GoogleSignIn.getClient(context, gso)

    suspend fun handleSignInResult(account: GoogleSignInAccount): String? =
        withContext(Dispatchers.IO) {
            try {
                val idToken = account.idToken
                if (idToken == null) {
                    Log.e("AUTH", "No ID token in Google account")
                    return@withContext null
                }

                val url = "${BuildConfig.SERVER_URL}/auth/google"
                val body = JSONObject().put("id_token", idToken).toString()
                    .toRequestBody("application/json".toMediaType())

                val req = Request.Builder()
                    .url(url)
                    .post(body)
                    .build()

                client.newCall(req).execute().use { res ->
                    val bodyStr = res.body?.string()
                    if (!res.isSuccessful) {
                        Log.e("AUTH", "Login failed: ${res.code}")
                        return@withContext null
                    }

                    val jwt = JSONObject(bodyStr ?: "").optString("token")
                    tokenManager.saveToken(jwt)
                    Log.d("AUTH", "JWT lagret: ${jwt.take(20)}...")
                    return@withContext jwt
                }
            } catch (e: Exception) {
                Log.e("AUTH", "Sign-in error", e)
                return@withContext null
            }
        }

    suspend fun registerDevice(fcmToken: String): Boolean =
        withContext(Dispatchers.IO) {
            val jwt = tokenManager.getToken()
            if (jwt == null) {
                Log.e("DEVICE", "Ingen JWT lagret – ikke innlogget?")
                return@withContext false
            }

            try {
                val url = "${BuildConfig.SERVER_URL}/profile/devices/register"
                val body = JSONObject()
                    .put("device_token", fcmToken)
                    .put(
                        "device_name",
                        "${android.os.Build.MANUFACTURER} - ${android.os.Build.MODEL}"
                    ).toString()
                    .toRequestBody("application/json".toMediaType())

                val req = Request.Builder()
                    .url(url)
                    .addHeader("Authorization", "Bearer $jwt")
                    .post(body)
                    .build()

                client.newCall(req).execute().use { res ->
                    val success = res.isSuccessful
                    Log.d("DEVICE", "Response ${res.code}: ${res.body?.string()}")
                    return@withContext success
                }
            } catch (e: Exception) {
                Log.e("DEVICE", "Device registration failed", e)
                return@withContext false
            }
        }
}
