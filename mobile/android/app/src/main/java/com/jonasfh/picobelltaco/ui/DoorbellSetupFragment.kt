package com.jonasfh.picobelltaco.ui

import android.Manifest
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
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

    private val seenDevices =
        mutableMapOf<String,
                android.bluetooth
                .BluetoothDevice>()

    private val callback = object : ScanCallback() {
        @RequiresPermission(
            Manifest.permission.BLUETOOTH_CONNECT
        )
        override fun onScanResult(
            type: Int,
            r: ScanResult
        ) {
            val name = r.device.name ?: return
            if (!name.startsWith("Picobell-")) return

            // Oppdater device-objektet uansett
            seenDevices[name] = r.device

            // UI-rad kun én gang
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

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    private fun startScan() {
        val mgr = requireContext()
            .getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val sc = mgr.adapter.bluetoothLeScanner

        seen.clear()
        deviceList?.removeAllViews()

        sc.startScan(callback)

        // Stopp scanning etter 6 sekunder
        deviceList?.postDelayed({
            try { sc.stopScan(callback) } catch (_: Exception) {}
            Log.d("SCAN", "Ble-scan stoppet etter timeout")
        }, 6000)
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
            setOnClickListener @androidx.annotation.RequiresPermission(
                android.Manifest.permission.BLUETOOTH_CONNECT
            ) {

                val ssid = ssidField?.text.toString()
                val pwd  = passField?.text.toString()
                val apiKey = BleProvisioner.generateApiKey()

                val device = seenDevices[name]!!

                // Først: hent MAC
                BleMacReader(requireContext(), device) { picoMac ->

                    Log.d("BLE", "MAC fra Pico: $picoMac")

                    createApartmentOnServer(
                        picoName = name,
                        apiKey = apiKey,
                        picoSerial = picoMac
                    ) {

                        // Når server er ferdig → start provisioning
                        BleProvisioner(
                            requireContext(),
                            device,
                            ssid,
                            pwd,
                            apiKey
                        ).start()
                    }

                }.start()
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

    private fun createApartmentOnServer(
        picoName: String,
        apiKey: String,
        picoSerial: String,
        onDone: () -> Unit
    ) {
        Thread {
            try {
                Log.d("HTTP", "Oppretter leilighet")
                val url = java.net.URL(
                    "https://picobell.no/profile/apartments"
                )
                val conn = url.openConnection() as java.net.HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val body = """
                {
                  "address": "Ny leilighet $picoName",
                  "pico_serial": "$picoSerial",
                  "api_key": "$apiKey"
                }
            """.trimIndent()

                conn.outputStream.use {
                    it.write(body.toByteArray())
                }

                val resp = conn.inputStream.bufferedReader().readText()
                Log.d("HTTP", "Apartment opprettet: $resp")

            } catch (e: Exception) {
                Log.e("HTTP", "Feil", e)
            }

            onDone()
        }.start()
    }

}

//TODO: Move to other location
private class BleProvisioner(
    val ctx: Context,
    val dev: android.bluetooth.BluetoothDevice,
    val ssid: String,
    val pwd: String,
    val deviceApiKey: String
) {

    private val uuidDevInfo =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a0")

    private val uuidDevId =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a1")

    private val uuidWifi =
        java.util.UUID.fromString(
            "12345678-1234-1234-1234-1234567890b0")

    private val uuidSsid =
        java.util.UUID.fromString(
            "12345678-1234-1234-1234-1234567890b1")

    private val uuidPwd =
        java.util.UUID.fromString(
            "12345678-1234-1234-1234-1234567890b2")

    private val uuidCmd =
        java.util.UUID.fromString(
            "12345678-1234-1234-1234-1234567890b3")

    private val uuidApi =
        java.util.UUID.fromString(
            "12345678-1234-1234-1234-1234567890b5"
        )


    private var gatt: android.bluetooth
    .BluetoothGatt? = null

    val apiKey = deviceApiKey

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun start() {

        gatt = dev.connectGatt(
            ctx,
            false,
            gattCb
        )
    }

    private val gattCb = object :
        android.bluetooth.BluetoothGattCallback() {

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onConnectionStateChange(
            g: BluetoothGatt,
            st: Int,
            new: Int
        ) {
            if (new ==
                BluetoothProfile.STATE_CONNECTED
            ) {
                g.discoverServices()
            }
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onServicesDiscovered(
            g: BluetoothGatt,
            st: Int
        ) {
            val svc = g.getService(uuidWifi)
            if (svc == null) {
                Log.e(
                    "BLE",
                    "Ingen WiFi-service"
                )
                return
            }

            val cSsid = svc.getCharacteristic(uuidSsid)
            val cPwd  = svc.getCharacteristic(uuidPwd)
            val cApi  = svc.getCharacteristic(uuidApi)
            val cCmd  = svc.getCharacteristic(uuidCmd)

            val devInfo = g.getService(uuidDevInfo)
            val cDevId = devInfo?.getCharacteristic(uuidDevId)
            val picoMac = cDevId?.value?.toString(Charsets.UTF_8) ?: ""


// Første step: SSID
            cSsid.value = ssid.toByteArray()
            g.writeCharacteristic(cSsid)

            step = 1
            this.cPwd = cPwd
            this.cApi = cApi       // NEW
            this.cCmd = cCmd
            this.g = g

        }

        private var step = 0
        private lateinit var cPwd:
                android.bluetooth.BluetoothGattCharacteristic
        private lateinit var cCmd:
                android.bluetooth.BluetoothGattCharacteristic
        private lateinit var g:
                android.bluetooth.BluetoothGatt
        private lateinit var cApi: BluetoothGattCharacteristic


        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onCharacteristicWrite(
            gatt: BluetoothGatt,
            ch:
            BluetoothGattCharacteristic,
            st: Int
        ) {
            if (step == 1) {
                cPwd.value = pwd.toByteArray()
                g.writeCharacteristic(cPwd)
                step = 2
                return
            }

            if (step == 2) {
                cApi.value = apiKey.toByteArray()   // NEW
                g.writeCharacteristic(cApi)
                step = 3
                return
            }

            if (step == 3) {
                cCmd.value = "connect".toByteArray()
                g.writeCharacteristic(cCmd)
                step = 4
                return
            }

            if (step == 4) {
                Log.d("BLE", "Provisioning ferdig")
                gatt.disconnect()
            }

        }
    }
    companion object {
        public fun generateApiKey(): String {
            val bytes = ByteArray(32)
            java.security.SecureRandom().nextBytes(bytes)
            return bytes.joinToString("") { "%02x".format(it) }
        }
    }
}


private class BleMacReader(
    val ctx: Context,
    val dev: android.bluetooth.BluetoothDevice,
    val onMacRead: (String) -> Unit
) {

    private val uuidDevInfo =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a0")
    private val uuidDevId =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a1")

    private var gatt: BluetoothGatt? = null

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun start() {
        gatt = dev.connectGatt(ctx, false, cb)
    }

    private val cb = object : BluetoothGattCallback() {

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onConnectionStateChange(g: BluetoothGatt, st: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                g.discoverServices()
            }
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onServicesDiscovered(g: BluetoothGatt, status: Int) {
            val svc = g.getService(uuidDevInfo)
            val ch  = svc?.getCharacteristic(uuidDevId)

            if (ch == null) {
                Log.e("BLE", "DevID characteristic mangler")
                g.disconnect()
                return
            }

            g.readCharacteristic(ch)
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onCharacteristicRead(
            g: BluetoothGatt,
            ch: BluetoothGattCharacteristic,
            status: Int
        ) {
            if (ch.uuid == uuidDevId) {
                val mac = ch.value.toString(Charsets.UTF_8)
                onMacRead(mac)
                g.disconnect()
            }
        }
    }
}
