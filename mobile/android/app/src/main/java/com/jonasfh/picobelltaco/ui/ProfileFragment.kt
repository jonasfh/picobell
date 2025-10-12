package com.jonasfh.picobelltaco.ui

import android.graphics.Typeface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.jonasfh.picobelltaco.R
import com.jonasfh.picobelltaco.auth.AuthManager

class ProfileFragment : Fragment() {

    private lateinit var authManager: AuthManager
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        authManager = AuthManager(requireContext())
    }

    override fun onCreateView(
        inflater: android.view.LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Hovedscroll
        val scrollView = ScrollView(requireContext())
        val layout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        }

        // Bruker-info
        val txtUser = TextView(requireContext()).apply {
            // text = "Bruker: ${authManager.getEmail() ?: "ukjent"}"
            text = "Bruker: jonasfh"
            textSize = 20f
            setTypeface(null, Typeface.BOLD)
            setPadding(0, 0, 0, 32)
        }
        layout.addView(txtUser)

        // Leiligheter
        layout.addView(sectionTitle("Leiligheter:"))
        val apartments = listOf("Parkveien 12", "Kirkeveien 3B")
        apartments.forEach { addr ->
            val addrView = TextView(requireContext()).apply {
                text = addr
                textSize = 16f
                setPadding(16, 8, 0, 8)
            }
            layout.addView(addrView)
        }

        // Devices
        layout.addView(sectionTitle("Devices:"))
        val devices = listOf("Pixel 8 Pro", "Galaxy Tab S9")
        devices.forEach { device ->
            layout.addView(deviceRow(device))
        }

        scrollView.addView(layout)
        return scrollView
    }

    /** Lager en enkel seksjonsoverskrift */
    private fun sectionTitle(title: String): TextView =
        TextView(requireContext()).apply {
            text = title
            textSize = 18f
            setTypeface(null, Typeface.BOLD)
            setPadding(0, 24, 0, 8)
        }

    /** Lager en rad med device-navn + slett og åpne-knapp */
    private fun deviceRow(name: String): LinearLayout {
        val row = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 8, 0, 8)
        }

        val txtName = TextView(requireContext()).apply {
            text = name
            textSize = 16f
            layoutParams = LinearLayout.LayoutParams(0,
                ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }

        val btnDelete = Button(requireContext()).apply {
            text = "🗑️"
            setOnClickListener {
                // TODO: Kall API for å slette device
            }
        }

        val btnOpen = Button(requireContext()).apply {
            text = "Åpne"
            isEnabled = false
        }

        // Eksempel: simuler “noen ringer på”
        row.postDelayed({
            btnOpen.isEnabled = true
            handler.postDelayed({ btnOpen.isEnabled = false }, 5000)
        }, 2000)

        row.addView(txtName)
        row.addView(btnDelete)
        row.addView(btnOpen)
        return row
    }
}
