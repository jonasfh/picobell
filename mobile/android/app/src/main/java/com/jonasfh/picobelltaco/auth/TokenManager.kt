package com.jonasfh.picobelltaco.auth

import android.content.Context
import androidx.core.content.edit
import androidx.preference.PreferenceManager

class TokenManager(context: Context) {

    companion object {
        private const val KEY_JWT = "jwt_token"
    }

    private val prefs = PreferenceManager.getDefaultSharedPreferences(context)

    fun saveToken(token: String) {
        prefs.edit {
            putString(KEY_JWT, token)
        }
    }

    fun getToken(): String? {
        return prefs.getString(KEY_JWT, null)
    }

    fun clearToken() {
        prefs.edit {
            remove(KEY_JWT)
        }
    }
}
