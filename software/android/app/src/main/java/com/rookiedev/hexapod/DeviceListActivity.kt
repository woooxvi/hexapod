package com.rookiedev.hexapod

import android.annotation.SuppressLint
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Bundle
import android.view.View
import android.view.Window
import android.widget.AdapterView.OnItemClickListener
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.TextView


/**
 * This Activity appears as a dialog. It lists any paired devices and
 * devices detected in the area after discovery. When a device is chosen
 * by the user, the MAC address of the device is sent back to the parent
 * Activity in the result Intent.
 */
class DeviceListActivity : Activity() {
    /**
     * Member fields
     */
    private var mBtAdapter: BluetoothAdapter? = null

    private var mContext: Context? = null
    private var bluetoothManager: BluetoothManager? = null

    /**
     * Newly discovered devices
     */
    private var mNewDevicesArrayAdapter: ArrayAdapter<String>? = null

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Setup the window
//        requestWindowFeature(Window.FEATURE_INDETERMINATE_PROGRESS)
        setContentView(R.layout.activity_device_list)

        mContext = applicationContext

        // Set result CANCELED in case the user backs out
        setResult(RESULT_CANCELED)

        // Initialize array adapters. One for already paired devices and
        // one for newly discovered devices
        val pairedDevicesArrayAdapter = ArrayAdapter<String>(this, R.layout.device_name)
        mNewDevicesArrayAdapter = ArrayAdapter(this, R.layout.device_name)

        // Find and set up the ListView for paired devices
        val pairedListView: ListView = findViewById<ListView>(R.id.paired_devices)
        pairedListView.adapter = pairedDevicesArrayAdapter
        pairedListView.onItemClickListener = mDeviceClickListener

        // Find and set up the ListView for newly discovered devices
//        val newDevicesListView: ListView = findViewById(R.id.new_devices)
//        newDevicesListView.adapter = mNewDevicesArrayAdapter
//        newDevicesListView.onItemClickListener = mDeviceClickListener

        // Register for broadcasts when a device is discovered
//        var filter = IntentFilter(BluetoothDevice.ACTION_FOUND)
//        this.registerReceiver(mReceiver, filter)

        // Register for broadcasts when discovery has finished
//        filter = IntentFilter(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)
//        this.registerReceiver(mReceiver, filter)

        // Get the local Bluetooth adapter
        bluetoothManager =
            mContext!!.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager!!.adapter

        // Get a set of currently paired devices
        val pairedDevices: Set<BluetoothDevice> = bluetoothManager!!.adapter.bondedDevices

        // If there are paired devices, add each one to the ArrayAdapter
        if (pairedDevices.isNotEmpty()) {
            findViewById<View>(R.id.title_paired_devices).visibility = View.VISIBLE
            for (device in pairedDevices) {
                pairedDevicesArrayAdapter.add(
                    """
                        ${device.name}
                        ${device.address}
                        """.trimIndent()
                )
            }
        } else {
            val noDevices = "No device"
            pairedDevicesArrayAdapter.add(noDevices)
        }
    }

    @SuppressLint("MissingPermission")
    override fun onDestroy() {
        super.onDestroy()

        // Make sure we're not doing discovery anymore
//        if (mBtAdapter != null) {
//            mBtAdapter!!.cancelDiscovery()
//        }
//        bluetoothManager!!.adapter.cancelDiscovery()

        // Unregister broadcast listeners
//        unregisterReceiver(mReceiver)
    }

    /**
     * The on-click listener for all devices in the ListViews
     */
    @SuppressLint("MissingPermission")
    private val mDeviceClickListener =
        OnItemClickListener { av, v, arg2, arg3 -> // Cancel discovery because it's costly and we're about to connect
//            bluetoothManager!!.adapter.cancelDiscovery()

            // Get the device MAC address, which is the last 17 chars in the View
            val info = (v as TextView).text.toString()
            val address = info.substring(info.length - 17)

            // Create the result Intent and include the MAC address
            val intent = Intent()
            intent.putExtra(EXTRA_DEVICE_ADDRESS, address)

            // Set result and finish this Activity
            setResult(RESULT_OK, intent)
            finish()
        }

    /**
     * The BroadcastReceiver that listens for discovered devices and changes the title when
     * discovery is finished
     */
    private val mReceiver: BroadcastReceiver = object : BroadcastReceiver() {
        @SuppressLint("MissingPermission")
        override fun onReceive(context: Context?, intent: Intent) {
            val action = intent.action

            // When discovery finds a device
            if (BluetoothDevice.ACTION_FOUND == action) {
                // Get the BluetoothDevice object from the Intent
                val device =
                    intent.getParcelableExtra<BluetoothDevice>(BluetoothDevice.EXTRA_DEVICE)
                // If it's already paired, skip it, because it's been listed already
                if (device != null && device.bondState != BluetoothDevice.BOND_BONDED) {
                    mNewDevicesArrayAdapter!!.add(
                        """
                            ${device.name}
                            ${device.address}
                            """.trimIndent()
                    )
                }
                // When discovery is finished, change the Activity title
//            } else if (BluetoothAdapter.ACTION_DISCOVERY_FINISHED == action) {
//                setProgressBarIndeterminateVisibility(false)
//                setTitle(R.string.select_device)
//                if (mNewDevicesArrayAdapter!!.count == 0) {
//                    val noDevices = resources.getText(R.string.none_found).toString()
//                    mNewDevicesArrayAdapter!!.add(noDevices)
//                }
            }
        }
    }

    companion object {
        /**
         * Tag for Log
         */
        private const val TAG = "DeviceListActivity"

        /**
         * Return Intent extra
         */
        var EXTRA_DEVICE_ADDRESS = "device_address"
    }
}