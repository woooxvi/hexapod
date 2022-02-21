package com.rookiedev.hexapod

import android.Manifest
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.InetAddresses.isNumericAddress
import android.os.Build
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.text.method.LinkMovementMethod
import android.view.View
import android.widget.*
import android.widget.AdapterView.OnItemClickListener
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.material.tabs.TabLayout
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout


class MainActivity : AppCompatActivity() {
    companion object {
        private const val BLUETOOTH_PERMISSION_CODE = 100
        private const val INTERNET_PERMISSION_CODE = 101
    }
    private val SHAREDPREFSNAME = "com.rookiedev.hexapod_preferences"
    private val SHAREDPREFSIP = "IP"
    private val SHAREDPREFSPORT = "PORT"

    private var mContext: Context?=null

    private lateinit var ipInput: TextInputEditText
    private lateinit var portInput: TextInputEditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        mContext = applicationContext

        ipInput = findViewById(R.id.ip_input)
        portInput = findViewById(R.id.port_input)
        val buttonConnect = findViewById<Button>(R.id.button_connect)

        val ipLayout = findViewById<TextInputLayout>(R.id.ip_input_layout)
        val portLayout = findViewById<TextInputLayout>(R.id.port_input_layout)

        val deviceList = findViewById<ListView>(R.id.paired_devices)

        val sourceLink = findViewById<TextView>(R.id.textView_github)
        sourceLink.movementMethod = LinkMovementMethod.getInstance()


        val tabLayout = findViewById<TabLayout>(R.id.tab)
        tabLayout.addOnTabSelectedListener(
            object : TabLayout.OnTabSelectedListener {
                @RequiresApi(Build.VERSION_CODES.S)
                override fun onTabSelected(tab: TabLayout.Tab?) {
                    if (tab!!.text == "WiFi") {
                        ipLayout.visibility = View.VISIBLE
                        portLayout.visibility = View.VISIBLE
                        deviceList.visibility = View.GONE
                    } else if (tab.text == "Bluetooth") {
                        checkPermission(Manifest.permission.BLUETOOTH_CONNECT, BLUETOOTH_PERMISSION_CODE)
                        if (ActivityCompat.checkSelfPermission(
                                mContext!!,
                                Manifest.permission.BLUETOOTH_CONNECT
                            ) != PackageManager.PERMISSION_GRANTED
                        ) {
                            // TODO: Consider calling
                            //    ActivityCompat#requestPermissions
                            // here to request the missing permissions, and then overriding
                            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                            //                                          int[] grantResults)
                            // to handle the case where the user grants the permission. See the documentation
                            // for ActivityCompat#requestPermissions for more details.
                            return
                        }
                        ipLayout.visibility = View.GONE
                        portLayout.visibility = View.GONE
                        deviceList.visibility = View.VISIBLE

                        // Initialize array adapters. One for already paired devices and
                        // one for newly discovered devices

                        // Initialize array adapters. One for already paired devices and
                        // one for newly discovered devices
                        val pairedDevicesArrayAdapter =
                            ArrayAdapter<kotlin.String>(mContext!!, R.layout.device_name)

                        // Find and set up the ListView for paired devices

                        // Find and set up the ListView for paired devices
                        val pairedListView = findViewById<ListView>(R.id.paired_devices)
                        pairedListView.adapter = pairedDevicesArrayAdapter
                        pairedListView.onItemClickListener = mDeviceClickListener

                        // Get the local Bluetooth adapter

                        // Get the local Bluetooth adapter
//                        mBtAdapter = BluetoothAdapter.getDefaultAdapter()
                        val bluetoothManager = mContext!!.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
                        bluetoothManager.adapter

                        // Get a set of currently paired devices

                        // Get a set of currently paired devices
                        val pairedDevices: Set<BluetoothDevice> = bluetoothManager.adapter.bondedDevices

                        // If there are paired devices, add each one to the ArrayAdapter

                        // If there are paired devices, add each one to the ArrayAdapter
                        if (pairedDevices.isNotEmpty()) {
//                            findViewById<View>(R.id.title_paired_devices).visibility = View.VISIBLE
                            for (device in pairedDevices) {
                                pairedDevicesArrayAdapter.add(
                                    """
                                    ${device.name}
                                    ${device.address}
                                    """.trimIndent()
                                )
                            }
                            pairedListView.layoutParams.height = 153*6
                        }
//                        else {
//                            val noDevices = resources.getText(R.string.none_paired).toString()
//                            pairedDevicesArrayAdapter.add(noDevices)
//                        }
                    }
                }

                override fun onTabUnselected(tab: TabLayout.Tab?) {
                }

                override fun onTabReselected(tab: TabLayout.Tab?) {
                }
            }
        )

        readSharedPref()

        buttonConnect.setOnClickListener {
            // your code to perform when the user clicks on the button

//            Toast.makeText(this@MainActivity, "You clicked me.", Toast.LENGTH_SHORT).show()
            if (isNumericAddress(ipInput.text.toString()) && portInput.text.toString()
                    .toInt() >= 0 && portInput.text.toString().toInt() <= 65535
            ) {
                saveSharedPref()
                val intent = Intent(this, ControlActivity::class.java).apply {
                    putExtra("ip", ipInput.text.toString())
                    putExtra("port", portInput.text.toString())
                }
                startActivity(intent)
            } else if (!isNumericAddress(ipInput.text.toString())) {
                ipLayout.error = getString(R.string.invalid_ip)
            } else {
                portLayout.error = getString(R.string.invalid_port)
            }
        }


        ipInput.addTextChangedListener(object : TextWatcher {
            override fun onTextChanged(s: CharSequence, start: Int, before: Int, count: Int) {
                ipLayout.error = null
            }

            override fun beforeTextChanged(s: CharSequence, start: Int, count: Int, after: Int) {}
            override fun afterTextChanged(s: Editable) {}
        })

        portInput.addTextChangedListener(object : TextWatcher {
            override fun onTextChanged(s: CharSequence, start: Int, before: Int, count: Int) {
                portLayout.error = null
            }

            override fun beforeTextChanged(s: CharSequence, start: Int, count: Int, after: Int) {}
            override fun afterTextChanged(s: Editable) {}
        })
    }

    // Function to check and request permission.
    private fun checkPermission(permission: String, requestCode: Int) {
        if (ActivityCompat.checkSelfPermission(this@MainActivity, permission) == PackageManager.PERMISSION_DENIED) {

            // Requesting the permission
            ActivityCompat.requestPermissions(this@MainActivity, arrayOf(permission), requestCode)
        } else {
            Toast.makeText(this@MainActivity, "Permission already granted", Toast.LENGTH_SHORT).show()
        }
    }

    // This function is called when the user accepts or decline the permission.
    // Request Code is used to check which permission called this function.
    // This request code is provided when the user is prompt for permission.
    override fun onRequestPermissionsResult(requestCode: Int,
                                            permissions: Array<String>,
                                            grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == BLUETOOTH_PERMISSION_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this@MainActivity, "Camera Permission Granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this@MainActivity, "Camera Permission Denied", Toast.LENGTH_SHORT).show()
            }
        } else if (requestCode == INTERNET_PERMISSION_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this@MainActivity, "Storage Permission Granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this@MainActivity, "Storage Permission Denied", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * The on-click listener for all devices in the ListViews
     */
    private val mDeviceClickListener =
        OnItemClickListener { av, v, arg2, arg3 -> // Cancel discovery because it's costly and we're about to connect
//            mBtAdapter.cancelDiscovery()
//
//            // Get the device MAC address, which is the last 17 chars in the View
//            val info = (v as TextView).text.toString()
//            val address = info.substring(info.length - 17)
//
//            // Create the result Intent and include the MAC address
//            val intent = Intent()
//            intent.putExtra(EXTRA_DEVICE_ADDRESS, address)
//
//            // Set result and finish this Activity
//            setResult(RESULT_OK, intent)
//            finish()
        }

    private fun readSharedPref() {
        val prefs = getSharedPreferences(
            SHAREDPREFSNAME,
            MODE_PRIVATE
        ) // get the parameters from the Shared
        // read values from the shared preferences
        ipInput.setText(prefs.getString(SHAREDPREFSIP, "192.168.1.127"))
        portInput.setText(prefs.getString(SHAREDPREFSPORT, "1234"))
    }

    private fun saveSharedPref() {
        val prefs = getSharedPreferences(
            SHAREDPREFSNAME,
            MODE_PRIVATE
        )
        val editor = prefs.edit()
        editor.putString(SHAREDPREFSIP, ipInput.text.toString())
        editor.putString(SHAREDPREFSPORT, portInput.text.toString())
        editor.apply()
    }
}