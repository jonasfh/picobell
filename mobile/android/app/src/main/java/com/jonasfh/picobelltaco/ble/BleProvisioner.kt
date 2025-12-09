package com.jonasfh.picobelltaco.ble

import android.Manifest
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothProfile
import android.content.Context
import android.util.Log
import androidx.annotation.RequiresPermission

class BleProvisioner(
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
