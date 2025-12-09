package com.jonasfh.picobelltaco.ble

import android.Manifest
import android.bluetooth.*
import android.content.Context
import android.util.Log
import androidx.annotation.RequiresPermission

class BleMacReader(
    val ctx: Context,
    val dev: BluetoothDevice,
    val onMacRead: (String) -> Unit
) {

    private val uuidDevInfo =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a0")
    private val uuidDevId =
        java.util.UUID.fromString("12345678-1234-1234-1234-1234567890a1")

    private var gatt: BluetoothGatt? = null

    @RequiresPermission(android.Manifest.permission.BLUETOOTH_CONNECT)
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
            val ch = svc?.getCharacteristic(uuidDevId)

            if (ch == null) {
                Log.e("BLE", "DevID characteristic mangler")
                g.disconnect()
                return
            }

            g.readCharacteristic(ch)
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onCharacteristicRead(
            g: BluetoothGatt, ch: BluetoothGattCharacteristic, status: Int
        ) {
            if (ch.uuid == uuidDevId) {
                val mac = ch.value.toString(Charsets.UTF_8)
                onMacRead(mac)
                g.disconnect()
            }
        }
    }
}
