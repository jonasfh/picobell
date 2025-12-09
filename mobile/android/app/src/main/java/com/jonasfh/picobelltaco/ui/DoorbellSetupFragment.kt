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
import com.jonasfh.picobelltaco.R

class DoorbellSetupFragment : Fragment(), HasMenu {

    private var ssidField: EditText? = null
    private var passField: EditText? = null
    private var deviceList: LinearLayout? = null

    private val seen = mutableSetOf<String>()

    private val requestLocation =
        registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { granted ->
            updateCurrentWifi()
            requestBlePermissions()
        }

    private val requestBle =
        registerForActivityResult(
            ActivityResultContracts.
            RequestMultiplePermissions()
        ) @androidx.annotation.RequiresPermission(android.Manifest.permission.BLUETOOTH_SCAN) { perms ->
            val ok = perms[Manifest.permission.
            BLUETOOTH_SCAN] == true
            if (ok) startScan()
        }

    private val callback = object : ScanCallback() {
        @RequiresPermission(
            Manifest.permission.BLUETOOTH_CONNECT
        )
        override fun onScanResult(type: Int,
                                  r: ScanResult) {
            val name = r.device.name ?: return
            if (!name.startsWith("Picobell-")) return

            if (seen.add(name)) addDevice(name)
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
        val layout = LinearLayout(requireContext())
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(50, 50, 50, 200)
        root.addView(layout)

        val title = TextView(requireContext())
        title.text =
            "Dørklokke-oppsett\n" +
            "(Koble til Pico via BLE)"
        title.textSize = 22f
        layout.addView(title)

        //
        // Wi-Fi SSID
        //
        val ssidLabel = TextView(requireContext())
        ssidLabel.text = "Du er på nettverket:"
        ssidLabel.textSize = 18f
        ssidLabel.setPadding(0, 30, 0, 10)
        layout.addView(ssidLabel)

        ssidField = EditText(requireContext()).apply {
            hint = "ssid"
        }
        layout.addView(ssidField)

        //
        // Wi-Fi passord
        //
        val passLabel = TextView(requireContext())
        passLabel.text = "Passord til nettverket:"
        passLabel.textSize = 18f
        passLabel.setPadding(0, 30, 0, 10)
        layout.addView(passLabel)

        passField = EditText(requireContext()).apply {
            hint = "wifi-passord"
            inputType = InputType.TYPE_CLASS_TEXT or
                    InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        layout.addView(passField)

        //
        // Pico devices
        //
        val devTitle = TextView(requireContext())
        devTitle.text = "Finner Picobell:"
        devTitle.textSize = 18f
        devTitle.setPadding(0, 40, 0, 10)
        layout.addView(devTitle)

        deviceList = LinearLayout(requireContext())
        deviceList!!.orientation =
            LinearLayout.VERTICAL
        layout.addView(deviceList)

        //
        // Save button
        //
        val btnSave = Button(requireContext()).apply {
            text = "Lagre og restart Picobell"
            setPadding(20, 20, 20, 20)
            setOnClickListener {
                Log.d("SETUP",
                    "Lagre: ssid=${ssidField?.text} " +
                            "pass=${passField?.text}")
            }
        }
        layout.addView(btnSave)

        //
        // Start permission chain
        //
        requestLocation.launch(
            Manifest.permission.ACCESS_FINE_LOCATION
        )

        return root
    }

    private fun updateCurrentWifi() {
        try {
            val wifi = requireContext().
            applicationContext.
            getSystemService(
                android.net.wifi.WifiManager::
                class.java
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

    @RequiresPermission(
        Manifest.permission.BLUETOOTH_SCAN
    )
    private fun startScan() {
        val mgr = requireContext().
        getSystemService(
            Context.BLUETOOTH_SERVICE
        ) as BluetoothManager
        val sc = mgr.adapter.bluetoothLeScanner

        seen.clear()
        deviceList?.removeAllViews()
        sc.startScan(callback)
    }

    private fun addDevice(name: String) {
        val row = LinearLayout(requireContext())
        row.orientation = LinearLayout.HORIZONTAL
        row.setPadding(0, 20, 0, 20)

        val txt = TextView(requireContext())
        txt.text = name
        txt.textSize = 18f
        txt.layoutParams = LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT,
            1f
        )
        row.addView(txt)

        val btn = Button(requireContext()).apply {
            text = "Koble til og sett info"
            setOnClickListener {
                val ssid = ssidField?.text.toString()
                val pass = passField?.text.toString()
                Log.d("SETUP",
                    "Provision til $name → " +
                            "ssid=$ssid pass=$pass")
            }
        }
        row.addView(btn)

        deviceList?.addView(row)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    override fun onDestroyView() {
        super.onDestroyView()
        try {
            val mgr = requireContext().
            getSystemService(
                Context.BLUETOOTH_SERVICE
            ) as BluetoothManager
            mgr.adapter.bluetoothLeScanner.stopScan(callback)
        } catch (e: Exception) {
            Log.e("SCAN", "Stop error", e)
        }
    }

    override fun onCreateOptionsMenu(
        m: Menu, i: MenuInflater
    ) { MainMenu.inflate(m, i) }

    override fun onOptionsItemSelected(
        item: MenuItem
    ): Boolean {
        return when (item.itemId) {
            R.id.menu_profile -> {
                parentFragmentManager.
                beginTransaction()
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

    override fun onMenuSelected(item: MenuItem)
            : Boolean = false
}
