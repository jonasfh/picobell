package com.jonasfh.picobelltaco.ui

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Typeface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.text.InputType
import android.util.Log
import android.view.Gravity
import android.view.Menu
import android.view.MenuInflater
import android.view.MenuItem
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.core.view.isGone
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.jonasfh.picobelltaco.data.DeviceRepository
import com.jonasfh.picobelltaco.data.ProfileRepository
import com.jonasfh.picobelltaco.data.ApartmentRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import com.jonasfh.picobelltaco.R

class ProfileFragment : Fragment() , HasMenu{

    private lateinit var repository: ProfileRepository
    private lateinit var deviceRepository: DeviceRepository

    private lateinit var apartmentRepository: ApartmentRepository
    private val handler = Handler(Looper.getMainLooper())

    // Her lagres alle åpne-knapper per leilighet-id
    private val apartmentButtons = mutableMapOf<Int, Button>()

    // Her lagres eventuelle timer-handlers per leilighet-id,
    // slik at de kan nullstilles ved ny aktivering
    private val apartmentTimers = mutableMapOf<Int, Runnable>()

    private val ringEventReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val aptId = intent?.getIntExtra("apartment_id", -1) ?: -1
            Log.d("PROFILE", "Ring event received")
            if (aptId != -1) {
                Log.d("PROFILE", "Ring event for apartment $aptId")
                enableOpenApartment(aptId)
            }
        }
    }
    override fun onStart() {
        super.onStart()
        Log.d("PROFILE", "Register receiver for ring events")
        ContextCompat.registerReceiver(
            requireContext(),
            ringEventReceiver,
            IntentFilter("PICOBELL_RING_EVENT"),
            ContextCompat.RECEIVER_NOT_EXPORTED
        )
    }
    override fun onStop() {
        super.onStop()
        requireContext().unregisterReceiver(ringEventReceiver)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)
        MainMenu.setup(this)
        repository = ProfileRepository(requireContext())
        deviceRepository = DeviceRepository(requireContext())
        apartmentRepository = ApartmentRepository(requireContext())
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
                    layout.addView(apartmentRow(apt.address, apt.id))
                }
            }

            val prefs = requireContext().getSharedPreferences("events", 0)
            val now = System.currentTimeMillis()
            Log.d("PROFILE", "Re-activating apt apartments from stored event")
            profile.apartments.forEach { apt ->
                Log.d("PROFILE", "Checking apt=${apt.id}")
                val ts = prefs.getLong("apt_${apt.id}", 0L)
                if (ts > 0 && now - ts < 180_000) {

                    enableOpenApartment(apt.id)
                    Log.d("PROFILE", "Re-activated apt=${apt.id} from stored event")
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

    private fun apartmentRow(address: String, id: Int): LinearLayout {
        val row = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 20, 0, 20)
        }


        val btnOpen = Button(requireContext()).apply {
            text = address
            isEnabled = false
            setOnClickListener {
                lifecycleScope.launch {
                    try {
                        val ok = apartmentRepository.openApartmentDoor(id)
                        // JSON-body

                        if (ok) {
                            Log.d("OPEN", "Dør åpnet for leilighet $id")
                            Toast.makeText(
                                requireContext(),
                                "Porttelefon aktivert, dør skal åpnes",
                                Toast.LENGTH_LONG
                            ).show()
                            // btn.isEnabled = false
                            // btn.text = "$address (åpnet)"
                        } else {
                            Log.e("OPEN", "Klarte ikke åpne dør for $id")
                            Toast.makeText(
                                requireContext(),
                                "Kunne ikke åpne dør",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    } catch (e: Exception) {
                        Log.e("OPEN", "Feil under åpning av dør $id", e)
                        Toast.makeText(
                            requireContext(),
                            "Kunne ikke åpne dør",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }

            setPadding(60, 60, 60, 60)
        }
        apartmentButtons.put(id, btnOpen)
        // btnChangeAddress is used to open a textbox txtChangeAddress to change the address. The
        // textbox is hidden by default, and hides the btnOpen when active. The textbox is shown
        // when btnChangeAddress is pressed. txtChangeAddress should be editable.
        val txtChangeAddress = android . widget . EditText(requireContext()).apply {
            visibility = View.GONE
            setText(address) // Pre-fill with the current address
            textSize = 18f   // Fix: changed from 1 to 18f so it is visible
            inputType = InputType.TYPE_CLASS_TEXT // Ensures standard text keyboard appears
            layoutParams = LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f
            )
        }
        val btnDelete = Button(requireContext()).apply {
            text = "🗑️"
            visibility = View.GONE
            setOnClickListener {
                lifecycleScope.launch {
                    val success = apartmentRepository.deleteApartment(id)
                    if (success) {
                        handler.post {
                            row.visibility = View.GONE
                        }
                    }
                    else {
                        Toast.makeText(
                            requireContext(),
                            "Kunne ikke slette leilighet",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }
        }
        val btnChangeAddress = Button(requireContext()).apply {
            text = "✏️"

            setOnClickListener {
                if (txtChangeAddress.isGone) {
                    txtChangeAddress.visibility = View.VISIBLE
                    btnDelete.visibility = View.VISIBLE
                    btnOpen.visibility = View.GONE
                } else {
                    // log info
                    Log.d("PROFILE", "Changing address to ${txtChangeAddress.text}")

                    lifecycleScope.launch {
                        Log.d("PROFILE", "Lifecycle scope launched")
                        if (apartmentRepository.changeApartmentAddress(id, txtChangeAddress.text.toString())) {
                            Log.d("PROFILE", "Address changed ${txtChangeAddress.text}")
                            btnOpen.text = txtChangeAddress.text.toString()
                        }
                        else {
                            Log.e("PROFILE", "Failed to change address")
                            Toast.makeText(
                                requireContext(),
                                "Kunne ikke endre adressen",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                        txtChangeAddress.visibility = View.GONE
                        btnOpen.visibility = View.VISIBLE
                        btnDelete.visibility = View.GONE
                    }
                }
            }
        }



        row.addView(btnOpen)
        row.addView(txtChangeAddress)
        row.addView(btnChangeAddress)
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

    private fun enableOpenApartment(id: Int) {
        val btn = apartmentButtons[id]
        if (btn == null) {
            Log.w("PROFILE", "Fant ingen leilighet med id=$id")
            return
        }

        val originalText = btn.text.toString()

        // Hvis det finnes en aktiv timer, fjern den før vi starter ny
        apartmentTimers[id]?.let { existing ->
            handler.removeCallbacks(existing)
            Log.d("PROFILE", "Nullstiller eksisterende timer for leilighet $id")
        }

        // Enable knappen
        btn.isEnabled = true
        btn.text = "$originalText (aktivert)"
        Log.d("PROFILE", "Aktiverte knapp for leilighet $id")

        // Lag et nytt Runnable-objekt for disable
        val disableRunnable = Runnable {
            btn.isEnabled = false
            btn.text = originalText
            Log.d("PROFILE", "Deaktiverte knapp for leilighet $id (timeout)")
            apartmentTimers.remove(id)
        }

        // Lagre og start timer på nytt (180 sek)
        apartmentTimers[id] = disableRunnable
        handler.postDelayed(disableRunnable, 180_000)
    }

    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        MainMenu.inflate(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.menu_profile -> {
                // allerede på denne siden
                return true
            }
            R.id.menu_doorbell -> {
                parentFragmentManager.beginTransaction()
                    .replace(
                        (view?.parent as ViewGroup).id,
                        DoorbellSetupFragment()
                    )
                    .addToBackStack(null)
                    .commit()
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }
    override fun onMenuSelected(item: MenuItem): Boolean = false
}
