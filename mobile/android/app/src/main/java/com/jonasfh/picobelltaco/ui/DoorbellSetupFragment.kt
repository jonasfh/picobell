package com.jonasfh.picobelltaco.ui

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.*
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresPermission
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.jonasfh.picobelltaco.R

class DoorbellSetupFragment : Fragment(), HasMenu {

    private var scanLayout: LinearLayout? = null
    private val seenDevices = mutableSetOf<String>()

    private val requestLocation =
        registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { granted ->
            updateCurrentWifi()
            // Nå er location ferdig → be om BLE-permissions
            requestBlePermissions()
        }


    private val scanPermission =
        registerForActivityResult(
            androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions()
        ) @androidx.annotation.RequiresPermission(android.Manifest.permission.BLUETOOTH_SCAN) { perms ->
            val ok = perms[Manifest.permission.BLUETOOTH_SCAN] == true
            if (ok) startScan()
        }

    private val scanCallback = object : ScanCallback() {
        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val name = result.device.name ?: return
            if (!name.startsWith("Picobell-")) return

            if (seenDevices.add(name)) {
                Log.d("SCAN", "Fant Pico: $name")
                addDeviceRow(name)
            }
        }
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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
        scanLayout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, 40, 0, 0)
        }
        layout.addView(scanLayout)

        requestLocation.launch(android.Manifest.permission.ACCESS_FINE_LOCATION)

        return layout
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    override fun onDestroyView() {
        super.onDestroyView()

        // Stop scan for sikkerhets skyld
        try {
            val manager =
                requireContext().getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
            manager.adapter.bluetoothLeScanner.stopScan(scanCallback)
        } catch (e: Exception) {
            Log.e("SCAN", "Feil ved stopScan", e)
        }
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
    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    private fun startScan() {
        val manager =
            requireContext().getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val adapter = manager.adapter
        val scanner = adapter.bluetoothLeScanner

        seenDevices.clear()
        scanLayout?.removeAllViews()

        Log.d("SCAN", "Starter BLE-scan…")
        scanner.startScan(scanCallback)
    }

    private fun addDeviceRow(name: String) {
        val row = TextView(requireContext()).apply {
            text = name
            textSize = 20f
            setPadding(20, 20, 20, 20)
            setOnClickListener {
                Log.d("SCAN", "Klikk på $name — connect kommer senere")
            }
        }
        scanLayout?.addView(row)
    }
    private fun requestBlePermissions() {
        scanPermission.launch(
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT
            )
        )
    }

}
