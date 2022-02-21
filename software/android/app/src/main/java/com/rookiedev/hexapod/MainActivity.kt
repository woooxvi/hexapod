package com.rookiedev.hexapod

import android.Manifest
import android.app.Activity
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
import android.widget.AdapterView.OnItemClickListener
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.core.app.ActivityCompat
import com.google.android.material.tabs.TabLayout
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout


class MainActivity : AppCompatActivity() {
    companion object {
        private const val BLUETOOTH_PERMISSION_CODE = 100
        private const val INTERNET_PERMISSION_CODE = 101
    }

    private val REQUEST_CONNECT_DEVICE_SECURE = 1
    private val REQUEST_CONNECT_DEVICE_INSECURE = 2
    private val REQUEST_ENABLE_BT = 3

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
        val selectedDevice = findViewById<ConstraintLayout>(R.id.selected)
        val deviceName = findViewById<TextView>(R.id.textView_device_name)
        val deviceAddress = findViewById<TextView>(R.id.textView_device_address)

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
                        selectedDevice.visibility = View.GONE
                    } else if (tab.text == "Bluetooth") {
                        ipLayout.visibility = View.GONE
                        portLayout.visibility = View.GONE
                        deviceList.visibility = View.VISIBLE
                        selectedDevice.visibility = View.VISIBLE
                    }
                }

                override fun onTabUnselected(tab: TabLayout.Tab?) {
                }

                override fun onTabReselected(tab: TabLayout.Tab?) {
                }
            }
        )

        selectedDevice.setOnClickListener{
            checkPermission(Manifest.permission.BLUETOOTH_CONNECT, BLUETOOTH_PERMISSION_CODE)
            val serverIntent = Intent(this, DeviceListActivity::class.java)
            resultLauncher.launch(serverIntent)
//            startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE_INSECURE)
        }

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

    var resultLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            // There are no request codes
            val data: Intent? = result.data
//            doSomeOperations()
        }
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