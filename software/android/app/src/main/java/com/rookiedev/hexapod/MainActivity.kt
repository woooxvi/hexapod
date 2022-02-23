package com.rookiedev.hexapod

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.InetAddresses.isNumericAddress
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.text.method.LinkMovementMethod
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.core.app.ActivityCompat
import com.google.android.material.tabs.TabLayout
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout


class MainActivity : AppCompatActivity() {
    companion object {
        private const val BLUETOOTH_PERMISSION_CODE = 100
        private const val BLUETOOTH_SCAN_CODE = 101

        private const val SHARED_PREFS_NAME = "com.rookiedev.hexapod_preferences"
        private const val SHARED_PREFS_IP = "IP"
        private const val SHARED_PREFS_PORT = "PORT"
        private const val SHARED_PREFS_TAB = "TAB"
        private const val SHARED_PREFS_DEVICE_NAME = "DEVICE_NAME"
        private const val SHARED_PREFS_DEVICE_ADDRESS = "DEVICE_ADDRESS"
    }

    private var mContext: Context? = null

    private lateinit var ipInput: TextInputEditText
    private lateinit var portInput: TextInputEditText

    private lateinit var btDeviceName: TextView
    private lateinit var btDeviceMac: TextView

    private lateinit var tabLayout: TabLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        mContext = applicationContext

        // TCP
        val ipLayout = findViewById<TextInputLayout>(R.id.ip_input_layout)
        val portLayout = findViewById<TextInputLayout>(R.id.port_input_layout)
        ipInput = findViewById(R.id.ip_input)
        portInput = findViewById(R.id.port_input)

        // Bluetooth
        val selectedDevice = findViewById<ConstraintLayout>(R.id.selected)
        btDeviceName = findViewById(R.id.textView_device_name)
        btDeviceMac = findViewById(R.id.textView_device_mac)
        

        val buttonConnect = findViewById<Button>(R.id.button_connect)

        val sourceLink = findViewById<TextView>(R.id.textView_github)
        sourceLink.movementMethod = LinkMovementMethod.getInstance()

        tabLayout = findViewById(R.id.tab)

        tabLayout.addOnTabSelectedListener(
            object : TabLayout.OnTabSelectedListener {
                override fun onTabSelected(tab: TabLayout.Tab?) {
                    if (tab!!.text == "WiFi") {
                        ipLayout.visibility = View.VISIBLE
                        portLayout.visibility = View.VISIBLE
                        selectedDevice.visibility = View.GONE
                    } else if (tab.text == "Bluetooth") {
                        ipLayout.visibility = View.GONE
                        portLayout.visibility = View.GONE
                        selectedDevice.visibility = View.VISIBLE
                    }
                }

                override fun onTabUnselected(tab: TabLayout.Tab?) {
                }

                override fun onTabReselected(tab: TabLayout.Tab?) {
                }
            }
        )

        selectedDevice.setOnClickListener {
            checkPermission("android.permission.BLUETOOTH_CONNECT", BLUETOOTH_PERMISSION_CODE)
            checkPermission("android.permission.BLUETOOTH_SCAN", BLUETOOTH_SCAN_CODE)
            val serverIntent = Intent(this, DeviceListActivity::class.java)
            resultLauncher.launch(serverIntent)
//            startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE_INSECURE)
        }

        readSharedPref()

        if (tabLayout.selectedTabPosition == 0) {
            ipLayout.visibility = View.VISIBLE
            portLayout.visibility = View.VISIBLE
            selectedDevice.visibility = View.GONE
        } else if (tabLayout.selectedTabPosition == 1) {
            checkPermission("android.permission.BLUETOOTH_CONNECT", BLUETOOTH_PERMISSION_CODE)
            ipLayout.visibility = View.GONE
            portLayout.visibility = View.GONE
            selectedDevice.visibility = View.VISIBLE
        }

        buttonConnect.setOnClickListener {
            // your code to perform when the user clicks on the button

//            Toast.makeText(this@MainActivity, "You clicked me.", Toast.LENGTH_SHORT).show()
            if (tabLayout.selectedTabPosition == 0) {
                if (isNumericAddress(ipInput.text.toString()) && portInput.text.toString()
                        .toInt() >= 0 && portInput.text.toString().toInt() <= 65535
                ) {
                    saveSharedPref()
                    val intent = Intent(this, ControlActivity::class.java).apply {
                        putExtra("interface", "WiFi")
                        putExtra("ip", ipInput.text.toString())
                        putExtra("port", portInput.text.toString())
                    }
                    startActivity(intent)
                } else if (!isNumericAddress(ipInput.text.toString())) {
                    ipLayout.error = getString(R.string.invalid_ip)
                } else {
                    portLayout.error = getString(R.string.invalid_port)
                }
            } else if (tabLayout.selectedTabPosition == 1) {
                if (btDeviceMac.text.isNotBlank()) {
                    saveSharedPref()
                    val intent = Intent(this, ControlActivity::class.java).apply {
                        putExtra("interface", "Bluetooth")
                        putExtra("mac", btDeviceMac.text.toString())
                    }
                    startActivity(intent)
                }
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

    private var resultLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                // There are no request codes
                val data: Intent? = result.data

                btDeviceName.text = data!!.getStringExtra("device_name")
                btDeviceMac.text = data.getStringExtra("device_address")

            }
        }

    // Function to check and request permission.
    private fun checkPermission(permission: String, requestCode: Int) {
        if (ActivityCompat.checkSelfPermission(
                this@MainActivity,
                permission
            ) == PackageManager.PERMISSION_DENIED
        ) {
            // Requesting the permission
            ActivityCompat.requestPermissions(this@MainActivity, arrayOf(permission), requestCode)
        } else {
//            Toast.makeText(this@MainActivity, "Permission already granted", Toast.LENGTH_SHORT)
//                .show()

        }
    }

    // This function is called when the user accepts or decline the permission.
    // Request Code is used to check which permission called this function.
    // This request code is provided when the user is prompt for permission.
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == BLUETOOTH_PERMISSION_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(
                    this@MainActivity,
                    "Bluetooth Permission Granted",
                    Toast.LENGTH_SHORT
                )
                    .show()
            } else {
                Toast.makeText(this@MainActivity, "Bluetooth Permission Denied", Toast.LENGTH_SHORT)
                    .show()
            }
        }
    }

    override fun onPause() {
        super.onPause()
        saveSharedPref()
    }


    private fun readSharedPref() {
        val prefs = getSharedPreferences(
            SHARED_PREFS_NAME,
            MODE_PRIVATE
        ) // get the parameters from the Shared
        // read values from the shared preferences
        ipInput.setText(prefs.getString(SHARED_PREFS_IP, "192.168.1.127"))
        portInput.setText(prefs.getString(SHARED_PREFS_PORT, "1234"))

        val selectedTab = prefs.getString(SHARED_PREFS_TAB, "WiFi")
        if (selectedTab == "WiFi") {
            val tab = tabLayout.getTabAt(0)
            tab!!.select()
        } else if (selectedTab == "Bluetooth") {
            val tab = tabLayout.getTabAt(1)
            tab!!.select()
        }

        btDeviceName.text = prefs.getString(SHARED_PREFS_DEVICE_NAME, "Click to select a device")
        btDeviceMac.text = prefs.getString(SHARED_PREFS_DEVICE_ADDRESS, "")
    }

    private fun saveSharedPref() {
        val prefs = getSharedPreferences(
            SHARED_PREFS_NAME,
            MODE_PRIVATE
        )
        val editor = prefs.edit()
        editor.putString(SHARED_PREFS_IP, ipInput.text.toString())
        editor.putString(SHARED_PREFS_PORT, portInput.text.toString())
        if (tabLayout.selectedTabPosition == 0) {
            editor.putString(SHARED_PREFS_TAB, "WiFi")
        } else if (tabLayout.selectedTabPosition == 1) {
            editor.putString(SHARED_PREFS_TAB, "Bluetooth")
        }

        editor.putString(SHARED_PREFS_DEVICE_NAME, btDeviceName.text.toString())
        editor.putString(SHARED_PREFS_DEVICE_ADDRESS, btDeviceMac.text.toString())

        editor.apply()
    }
}