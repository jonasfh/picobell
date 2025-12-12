package com.jonasfh.picobelltaco

import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.util.TypedValue
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.widget.FrameLayout
import android.widget.LinearLayout
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
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

        // 1. Create a Root Layout (Vertical Linear Layout)
        val rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        }
        // 2. Create the Toolbar
        val toolbar = Toolbar(this).apply {
            // Give it a background color (using primary color usually looks best)
            val typedValue = TypedValue()
            theme.resolveAttribute(androidx.appcompat.R.attr.colorPrimary, typedValue, true)
            setBackgroundColor(typedValue.data)

            // Text color for title
            setTitleTextColor(android.graphics.Color.WHITE)
        }
        // 3. Create the Fragment Container (This is what you had before)
        val container = FrameLayout(this).apply { id = R.id.main_container }

        // 4. Add views to Root
        // Add Toolbar at the top
        rootLayout.addView(toolbar, LinearLayout.LayoutParams(MATCH_PARENT,
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 56f, resources.displayMetrics).toInt()
        ))

        // Add Fragment Container filling the rest of the space (weight = 1)
        rootLayout.addView(container, LinearLayout.LayoutParams(MATCH_PARENT, 0, 1f))

        // 5. Set Content View
        setContentView(rootLayout)

        // 6. IMPORTANT: Tell Android to use this toolbar as the Action Bar
        setSupportActionBar(toolbar)

        // ... The rest of your existing code (deviceRepository, permissions, etc.) ...

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
