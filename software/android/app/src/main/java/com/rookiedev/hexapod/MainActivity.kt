package com.rookiedev.hexapod

import android.content.Intent
import android.net.InetAddresses.isNumericAddress
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.text.method.LinkMovementMethod
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import java.lang.String
import kotlin.CharSequence
import kotlin.Int
import kotlin.apply
import kotlin.toString


class MainActivity : AppCompatActivity() {
    private val SHAREDPREFSNAME = "com.rookiedev.hexapod_preferences"
    private val SHAREDPREFSIP = "IP"
    private val SHAREDPREFSPORT = "PORT"

    private lateinit var ipInput:TextInputEditText
    private lateinit var portInput:TextInputEditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        ipInput = findViewById(R.id.ip_input)
        portInput = findViewById(R.id.port_input)
        val buttonConnect = findViewById<Button>(R.id.button_connect)

        val ipLayout = findViewById<TextInputLayout>(R.id.ip_input_layout)
        val portLayout = findViewById<TextInputLayout>(R.id.port_input_layout)

        val sourceLink = findViewById<TextView>(R.id.textView_github)
        sourceLink.movementMethod = LinkMovementMethod.getInstance()

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