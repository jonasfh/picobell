package com.jonasfh.picobelltaco

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        Log.d("FCM", "Message received: ${message.data}")
    }

    override fun onNewToken(token: String) {
        Log.d("FCM", "New token: $token")
    }
}
