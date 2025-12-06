package com.jonasfh.picobelltaco.auth

import android.Manifest
import android.R
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresPermission
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.edit
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.jonasfh.picobelltaco.MainActivity

class PicobellFirebaseMessagingService : FirebaseMessagingService() {

    @RequiresPermission(Manifest.permission.POST_NOTIFICATIONS)
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        Log.d("FCM", "Message received from: ${remoteMessage.from}")
        Log.d("FCM", "Message data: ${remoteMessage.data}")


        // Notification payload
        showNotification("Ding dong", "Noen ringer på ${remoteMessage.data["address"]}")

        // Save data payload indexed by apartment id
        val aptId = remoteMessage.data["apartment_id"]?.toIntOrNull()
        if (aptId != null) {
            val prefs = getSharedPreferences("events", MODE_PRIVATE)
            prefs.edit {
                putLong("apt_$aptId", System.currentTimeMillis())
            }

            val intent = Intent("PICOBELL_RING_EVENT").apply {
                putExtra("apartment_id", aptId)
                setPackage(packageName)   // 🔥 viktig for Android 12+
            }
            sendBroadcast(intent)
            Log.d("FCM", "Broadcasted ring event for apartment $aptId")
            Log.d("FCM", "Broadcast intent targets package: $packageName")
            Log.d("FCM", "Saved ring event for apt $aptId")
        }
    }

    @RequiresPermission(Manifest.permission.POST_NOTIFICATIONS)
    private fun showNotification(title: String?, message: String?) {
        val channelId = "picobell_channel"
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("from_notification", true)
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val notificationManager =
            getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

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
            .setContentIntent(pendingIntent)   // <<< åpner appen
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(this).notify(1, notification)
    }

    override fun onNewToken(token: String) {
        Log.d("FCM", "Refreshed token: $token")
    }
}