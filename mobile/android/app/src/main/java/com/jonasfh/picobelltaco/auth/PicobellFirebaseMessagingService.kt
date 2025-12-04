package com.jonasfh.picobelltaco.auth

import android.Manifest
import android.R
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresPermission
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class PicobellFirebaseMessagingService : FirebaseMessagingService() {

    @RequiresPermission(Manifest.permission.POST_NOTIFICATIONS)
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        Log.d("FCM", "Message received from: ${remoteMessage.from}")

        // Notification payload
        remoteMessage.notification?.let {
            showNotification(it.title, it.body)
        }

        val aptId = remoteMessage.data["apartment_id"]?.toIntOrNull()
        if (aptId != null) {
            val intent = Intent("PICOBELL_RING_EVENT").apply {
                putExtra("apartment_id", aptId)
                setPackage(packageName)   // 🔥 viktig for Android 12+
            }
            sendBroadcast(intent)
            Log.d("FCM", "Broadcasted ring event for apartment $aptId")
            Log.d("FCM", "Broadcast intent targets package: $packageName")
        }
    }

    @RequiresPermission(Manifest.permission.POST_NOTIFICATIONS)
    private fun showNotification(title: String?, message: String?) {
        val channelId = "picobell_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Picobell Notifications",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(NotificationManager::class.java)

            manager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle(title ?: "Doorbell")
            .setContentText(message ?: "Noen ringer på!")
            .setSmallIcon(R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(this).notify(1, notification)
    }

    override fun onNewToken(token: String) {
        Log.d("FCM", "Refreshed token: $token")
    }
}