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
                Log.d("AUTH", "Got ID token: ${idToken?.take(20)}...")

                if (idToken == null) {
                    Log.e("AUTH", "No ID token in Google account")
                    return@withContext null
                }

                val url = "${BuildConfig.SERVER_URL}/auth/google"
                Log.d("AUTH", "Posting token to $url")

                val body = JSONObject().put("id_token", idToken).toString()
                    .toRequestBody("application/json".toMediaType())
                Log.d("AUTH", JSONObject().put("id_token", idToken).toString())
                val req = Request.Builder()
                    .url(url)
                    .post(body)
                    .build()

                client.newCall(req).execute().use { res ->
                    val bodyStr = res.body?.string()
                    Log.d("AUTH", "Response ${res.code}: $bodyStr")

                    if (!res.isSuccessful) {
                        Log.e("AUTH", "Login failed: ${res.code}")
                        return@withContext null
                    }

                    val json = JSONObject(bodyStr ?: "")
                    val jwt = json.optString("token")
                    Log.d("AUTH", "Received JWT: ${jwt.take(20)}...")
                    return@withContext jwt
                }
            } catch (e: Exception) {
                Log.e("AUTH", "Sign-in error", e)
                return@withContext null
            }
        }

    suspend fun registerDevice(jwt: String, fcmToken: String): Boolean =
        withContext(Dispatchers.IO) {
            Log.d("DEVICE", "FCM: ${fcmToken.take(10)}... JWT ${jwt.take(10)}...")
            try {
                val url = "${BuildConfig.SERVER_URL}/profile/devices/register"
                Log.d("DEVICE", "Registering device at $url")
                Log.d("DEVICE", "Device name: ${android.os.Build.MANUFACTURER} - ${android.os.Build.MODEL}")
                val body = JSONObject()
                    .put("token", fcmToken)
                    .put("name", "${android.os.Build.MANUFACTURER} - ${android.os.Build.MODEL}")
                    .toString()
                    .toRequestBody("application/json".toMediaType())

                val req = Request.Builder()
                    .url(url)
                    .addHeader("Authorization", "Bearer $jwt")
                    .post(body)
                    .build()

                client.newCall(req).execute().use { res ->
                    val success = res.isSuccessful
                    val responseBody = res.body?.string()
                    Log.d("DEVICE", "Response ${res.code}: $responseBody")
                    return@withContext success
                }
            } catch (e: Exception) {
                Log.e("DEVICE", "Device registration failed", e)
                return@withContext false
            }
        }
}
