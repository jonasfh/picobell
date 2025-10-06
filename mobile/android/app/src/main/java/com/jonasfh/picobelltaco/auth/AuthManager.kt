package com.jonasfh.picobelltaco.auth

import android.content.Context
import android.util.Log
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.jonasfh.picobelltaco.BuildConfig
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject


class AuthManager(private val context: Context) {

    private val client = OkHttpClient()

    private val gso = GoogleSignInOptions.Builder(
        GoogleSignInOptions.DEFAULT_SIGN_IN
    ).requestIdToken("${BuildConfig.OAUTH2_CLIENT_ID}.apps.googleusercontent.com")
        .requestEmail()
        .build()

    val signInClient: GoogleSignInClient =
        GoogleSignIn.getClient(context, gso)

    suspend fun handleSignInResult(account: GoogleSignInAccount): String? {
        val idToken = account.idToken ?: return null
        val url = "${BuildConfig.SERVER_URL}/auth/google"

        val body = JSONObject().put("token", idToken).toString()
            .toRequestBody("application/json".toMediaType())

        val req = Request.Builder()
            .url(url)
            .post(body)
            .build()

        client.newCall(req).execute().use { res ->
            if (!res.isSuccessful) {
                Log.e("AUTH", "Login failed: ${res.code}")
                return null
            }
            val json = JSONObject(res.body?.string() ?: "")
            return json.optString("token") // f.eks. JWT fra backend
        }
    }

    suspend fun registerDevice(jwt: String, fcmToken: String): Boolean {
        val url = "${BuildConfig.SERVER_URL}/profile/devices/register"

        val body = JSONObject()
            .put("fcm_token", fcmToken)
            .put("device_model", android.os.Build.MODEL)
            .toString()
            .toRequestBody("application/json".toMediaType())

        val req = Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer $jwt")
            .post(body)
            .build()

        client.newCall(req).execute().use { res ->
            return res.isSuccessful
        }
    }

}
