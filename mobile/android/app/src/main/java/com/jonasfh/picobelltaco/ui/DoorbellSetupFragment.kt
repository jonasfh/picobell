package com.jonasfh.picobelltaco.ui

import android.os.Bundle
import android.util.Log
import android.view.*
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.jonasfh.picobelltaco.R

class DoorbellSetupFragment : Fragment(), HasMenu {


    private val requestLocation =
        registerForActivityResult(
            androidx.activity.result.contract.ActivityResultContracts.RequestPermission()
        ) { granted ->
            if (granted) {
                updateCurrentWifi()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)
        MainMenu.setup(this)
    }

    private var ssidLabel: TextView? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val layout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 50, 50, 50)
        }

        val txt = TextView(requireContext()).apply {
            text = "Dørklokke-oppsett\n(Koble til Pico via BLE)"
            textSize = 22f
        }
        layout.addView(txt)

        ssidLabel = TextView(requireContext()).apply {
            text = "Leser Wi-Fi..."
            textSize = 18f
            setPadding(0, 40, 0, 0)
        }
        layout.addView(ssidLabel)

        // Start permission request
        requestLocation.launch(android.Manifest.permission.ACCESS_FINE_LOCATION)

        return layout
    }

    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        MainMenu.inflate(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.menu_profile -> {
                parentFragmentManager.beginTransaction()
                    .replace(
                        (view?.parent as ViewGroup).id,
                        ProfileFragment()
                    )
                    .addToBackStack(null)
                    .commit()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onMenuSelected(item: MenuItem): Boolean = false

    private fun updateCurrentWifi() {
        try {
            val wifi = requireContext()
                .applicationContext
                .getSystemService(android.net.wifi.WifiManager::class.java)

            val info = wifi.connectionInfo
            val ssid = info?.ssid?.replace("\"", "") ?: "(ukjent)"

            ssidLabel?.text = "Tilkoblet Wi-Fi: $ssid"
        } catch (e: Exception) {
            ssidLabel?.text = "Kunne ikke lese Wi-Fi"
            Log.e("WIFI", "Feil", e)
        }
    }
}
