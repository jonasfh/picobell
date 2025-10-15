package com.jonasfh.picobelltaco.ui

import android.graphics.Typeface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.jonasfh.picobelltaco.data.DeviceRepository
import com.jonasfh.picobelltaco.data.ProfileRepository
import kotlinx.coroutines.launch

class ProfileFragment : Fragment() {

    private lateinit var repository: ProfileRepository
    private lateinit var deviceRepository: DeviceRepository
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository = ProfileRepository(requireContext())
        deviceRepository = DeviceRepository(requireContext())
    }

    override fun onCreateView(
        inflater: android.view.LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        Log.d("PROFILE", "Creating profile view")
        val scrollView = ScrollView(requireContext())
        val layout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        }

        // Midlertidig "Laster..."
        val txtLoading = TextView(requireContext()).apply {
            text = "Laster profil..."
            textSize = 18f
        }
        layout.addView(txtLoading)
        scrollView.addView(layout)

        // Start coroutine for å hente data
        lifecycleScope.launch {
            Log.d("PROFILE", "Fetching profile")
            val profile = repository.getProfile()
            layout.removeAllViews()

            if (profile == null) {
                Log.e("PROFILE", "Failed to fetch profile")
                val txtError = TextView(requireContext()).apply {
                    text = "Kunne ikke hente profil."
                    textSize = 18f
                }
                layout.addView(txtError)
                return@launch
            }
            Log.d("PROFILE", "Got profile: $profile")

            // Bruker-info
            val txtUser = TextView(requireContext()).apply {
                text = "Bruker: \n${profile.email}"
                textSize = 20f
                setTypeface(null, Typeface.BOLD)
                setPadding(0, 0, 0, 32)
            }
            layout.addView(txtUser)

            // Leiligheter
            layout.addView(sectionTitle("Leiligheter:"))
            if (profile.apartments.isEmpty()) {
                layout.addView(textLine("(ingen registrert)"))
            } else {
                profile.apartments.forEach { apt ->
                    layout.addView(apartmentRow(apt.address))
                }
            }

            // Devices
            layout.addView(sectionTitle("Devices:"))
            if (profile.devices.isEmpty()) {
                layout.addView(textLine("(ingen registrert)"))
            } else {
                profile.devices.forEach { dev ->
                    layout.addView(deviceRow(
                        dev.name, dev.modified_at, dev.id
                    ))
                }
            }
        }

        return scrollView
    }

    private fun sectionTitle(title: String): TextView =
        TextView(requireContext()).apply {
            text = title
            textSize = 18f
            setTypeface(null, Typeface.BOLD)
            setPadding(0, 24, 0, 8)
        }

    private fun textLine(text: String): TextView =
        TextView(requireContext()).apply {
            this.text = text
            textSize = 16f
            setPadding(16, 8, 0, 8)
        }

    private fun apartmentRow(address: String): LinearLayout {
        val row = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 20, 0, 20)
        }
        val btnOpen = Button(requireContext()).apply {
            text = address
            isEnabled = false
            setOnClickListener {
                // TODO: Kall API for å åpne leilighet
            }
            setPadding(60, 60, 60, 60)
        }

        val btnDelete = Button(requireContext()).apply {
            text = "🗑️"
            setOnClickListener {
                // TODO: Kall API for å slette leilighet
            }
        }

        row.addView(btnOpen)
        row.addView(btnDelete)
        return row
    }

    private fun deviceRow(name: String, modifiedAt: String, id: Int): LinearLayout {
        val row = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 8, 0, 8)
        }

        val txtName = TextView(requireContext()).apply {
            text = name
            textSize = 16f
            layoutParams = LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f
            )
        }
        val txtModifiedAt = TextView(requireContext()).apply {
            text = "Last seen: ${modifiedAt}"
            textSize = 12f
            layoutParams = LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f
            )
        }

        val btnDelete = Button(requireContext()).apply {
            text = "🗑️"
            setOnClickListener {
                lifecycleScope.launch {
                    val success = deviceRepository.deleteDevice(id)
                    if (success) {
                        handler.post {
                            row.visibility = View.GONE
                        }
                    }
                }
            }
            isEnabled = true
        }

        row.addView(txtName)
        row.addView(txtModifiedAt)
        row.addView(btnDelete)
        return row
    }
}
