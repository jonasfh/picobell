package com.jonasfh.picobelltaco.ui

import android.Manifest
import android.bluetooth.BluetoothManager
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.os.Bundle
import android.text.InputType
import android.util.Log
import android.view.*
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresPermission
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.jonasfh.picobelltaco.R
import com.jonasfh.picobelltaco.data.ApartmentRepository
import com.jonasfh.picobelltaco.ble.BleMacReader
import com.jonasfh.picobelltaco.ble.BleProvisioner
import kotlinx.coroutines.launch

class DoorbellSetupFragment : Fragment(), HasMenu {

    private var ssidField: EditText? = null
    private var passField: EditText? = null
    private var deviceList: LinearLayout? = null

    private val seenNames = mutableSetOf<String>()
    private val seenDevices =
        mutableMapOf<String, android.bluetooth.BluetoothDevice>()

    private val requestLocation =
        registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { granted ->
            updateCurrentWifi()
            requestBlePermissions()
        }

    private val requestBle =
        registerForActivityResult(
            ActivityResultContracts
                .RequestMultiplePermissions()
        ) @androidx.annotation.RequiresPermission(android.Manifest.permission.BLUETOOTH_SCAN) { perms ->
            val ok = perms[Manifest.permission.BLUETOOTH_SCAN] == true
            if (ok) startScan()
        }

    private val scanCallback = object : ScanCallback() {

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onScanResult(type: Int, res: ScanResult) {
            val name = res.device.name ?: return
            if (!name.startsWith("Picobell-")) return

            seenDevices[name] = res.device

            if (seenNames.add(name)) addDeviceRow(name)
        }
    }

    override fun onCreate(saved: Bundle?) {
        super.onCreate(saved)
        MainMenu.setup(this)
    }

    override fun onCreateView(
        inf: LayoutInflater,
        parent: ViewGroup?,
        state: Bundle?
    ): View {

        val root = ScrollView(requireContext())
        val layout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 50, 50, 200)
        }
        root.addView(layout)

        val title = TextView(requireContext()).apply {
            text = "Dørklokke-oppsett\n(Koble til Pico via BLE)"
            textSize = 22f
        }
        layout.addView(title)

        // --- WiFi SSID ---
        layout.addView(TextView(requireContext()).apply {
            text = "Du er på nettverket:"
            textSize = 18f
            setPadding(0, 30, 0, 10)
        })

        ssidField = EditText(requireContext()).apply {
            hint = "ssid"
        }
        layout.addView(ssidField)

        // --- WiFi password ---
        layout.addView(TextView(requireContext()).apply {
            text = "Passord til nettverket:"
            textSize = 18f
            setPadding(0, 30, 0, 10)
        })

        passField = EditText(requireContext()).apply {
            hint = "wifi-passord"
            inputType = InputType.TYPE_CLASS_TEXT or
                    InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        layout.addView(passField)

        // --- Ble devices ---
        layout.addView(TextView(requireContext()).apply {
            text = "Finner Picobell:"
            textSize = 18f
            setPadding(0, 40, 0, 10)
        })

        deviceList = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
        }
        layout.addView(deviceList)

        // Start permission chain
        requestLocation.launch(
            Manifest.permission.ACCESS_FINE_LOCATION
        )

        return root
    }

    private fun updateCurrentWifi() {
        try {
            val wifi = requireContext()
                .applicationContext
                .getSystemService(
                    android.net.wifi.WifiManager::class.java
                )

            val ssid = wifi.connectionInfo?.ssid
                ?.replace("\"", "") ?: ""

            ssidField?.setText(ssid)
        } catch (e: Exception) {
            Log.e("WIFI", "Feil", e)
        }
    }

    private fun requestBlePermissions() {
        requestBle.launch(
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT
            )
        )
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    private fun startScan() {
        val mgr = requireContext()
            .getSystemService(Context.BLUETOOTH_SERVICE)
                as BluetoothManager

        val scanner = mgr.adapter.bluetoothLeScanner

        seenNames.clear()
        deviceList?.removeAllViews()

        scanner.startScan(scanCallback)

        // Stop after 6 seconds
        deviceList?.postDelayed({
            try { scanner.stopScan(scanCallback) } catch (_: Exception) {}
        }, 6000)
    }

    private fun addDeviceRow(name: String) {
        val row = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 20, 0, 20)
        }

        row.addView(TextView(requireContext()).apply {
            text = name
            textSize = 18f
            layoutParams = LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f
            )
        })

        row.addView(Button(requireContext()).apply {
            text = "Koble til og sett info"

            setOnClickListener @androidx.annotation.RequiresPermission(android.Manifest.permission.BLUETOOTH_CONNECT) {

                val ssid = ssidField?.text.toString()
                val pwd = passField?.text.toString()
                val device = seenDevices[name]!!

                val aptRepo = ApartmentRepository(requireContext())

                // 1. Hent MAC
                BleMacReader(requireContext(), device) { picoMac ->

                    lifecycleScope.launch {

                        // 2. Opprett apartment
                        val apiKey = aptRepo.createApartment(
                            address = "Ny leilighet $name",
                            picoSerial = picoMac
                        )

                        if (apiKey == null) {
                            Toast.makeText(
                                requireContext(),
                                "Kunne ikke opprette leilighet",
                                Toast.LENGTH_LONG
                            ).show()
                            return@launch
                        }

                        // 3. Provisionér Pico
                        BleProvisioner(
                            requireContext(),
                            device,
                            ssid,
                            pwd,
                            apiKey
                        ).start()

                        Toast.makeText(
                            requireContext(),
                            "Leilighet opprettet og Pico konfigurert.",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }.start()
            }
        })

        deviceList?.addView(row)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    override fun onDestroyView() {
        super.onDestroyView()
        try {
            val mgr = requireContext().getSystemService(
                Context.BLUETOOTH_SERVICE
            ) as BluetoothManager

            mgr.adapter.bluetoothLeScanner.stopScan(scanCallback)
        } catch (e: Exception) {}
    }

    // --- Menu ---
    override fun onCreateOptionsMenu(m: Menu, i: MenuInflater) {
        MainMenu.inflate(m, i)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.menu_profile -> {
                parentFragmentManager
                    .beginTransaction()
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
}
