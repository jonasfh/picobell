package com.jonasfh.picobelltaco

import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.FrameLayout
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.common.api.ApiException
import com.google.firebase.messaging.FirebaseMessaging
import com.jonasfh.picobelltaco.auth.AuthManager
import com.jonasfh.picobelltaco.ui.ProfileFragment
import com.jonasfh.picobelltaco.data.DeviceRepository
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await

class MainActivity : AppCompatActivity() {

    private lateinit var authManager: AuthManager
    private lateinit var deviceRepository: DeviceRepository
    val deviceName = "${Build.MANUFACTURER} ${Build.MODEL}"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enkel container i kode
        val container = FrameLayout(this).apply { id = R.id.main_container }
        setContentView(container)

        deviceRepository = DeviceRepository(this)

        // Request notification permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ActivityCompat.checkSelfPermission(
                    this,
                    android.Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                notificationPermissionLauncher.launch(android.Manifest.permission.POST_NOTIFICATIONS)
            } else {
                setupFcm()
            }
        } else {
            setupFcm()
        }

        authManager = AuthManager(this)
        startSignIn()
    }

    private val notificationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                setupFcm()
            } else {
                Log.w("FCM", "Notification permission denied")
            }
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
                            deviceRepository.registerDevice(fcmToken)
                        }
                        // Vis profilfragment
                        showProfile()
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

    private fun setupFcm() {
        // Log token for debugging
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val token = task.result
                Log.d("FCM", "FCM Token ready: $token")
            } else {
                Log.e("FCM", "Failed to fetch FCM token", task.exception)
            }
        }
    }

    private fun showProfile() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.main_container, ProfileFragment())
            .commitNow()
    }
}