package com.jonasfh.picobelltaco

import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.common.api.ApiException
import com.google.firebase.messaging.FirebaseMessaging
import com.jonasfh.picobelltaco.auth.AuthManager
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await

class MainActivity : AppCompatActivity() {

    private lateinit var authManager: AuthManager
    val deviceName = "${Build.MANUFACTURER} ${Build.MODEL}"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ActivityCompat.checkSelfPermission(
                    this,
                    android.Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),
                    1001
                )
            }
        }

        authManager = AuthManager(this)
        startSignIn()
    }

    private fun startSignIn() {
        val intent = authManager.signInClient.signInIntent
        signInLauncher.launch(intent)
    }

    private val signInLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val data = result.data
            val task = GoogleSignIn.getSignedInAccountFromIntent(data)
            try {
                val account = task.getResult(ApiException::class.java)
                lifecycleScope.launch {
                    val jwt = authManager.handleSignInResult(account)
                    if (jwt != null) {
                        val fcmToken = getFcmToken()
                        if (fcmToken != null) {
                            Log.d("DEVICE", "fcmToken: $fcmToken")
                            authManager.registerDevice(fcmToken)
                        }
                    }
                }
            } catch (e: ApiException) {
                Log.e("AUTH", "Google sign-in failed", e)
            }
        }

    private suspend fun getFcmToken(): String? {
        return try {
            FirebaseMessaging.getInstance().token.await()
        } catch (e: Exception) {
            Log.e("FCM", "Failed to get FCM token", e)
            null
        }
    }
}
