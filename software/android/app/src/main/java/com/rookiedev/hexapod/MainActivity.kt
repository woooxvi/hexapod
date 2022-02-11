package com.rookiedev.hexapod

import android.net.InetAddresses.isNumericAddress
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import com.google.android.material.textfield.TextInputEditText
import android.text.Editable

import android.text.TextWatcher




class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val ipInput = findViewById<TextInputEditText>(R.id.ip_input)
        val portInput = findViewById<TextInputEditText>(R.id.port_input)
        val buttonConnect = findViewById<Button>(R.id.button_connect)

        buttonConnect.setOnClickListener {
            // your code to perform when the user clicks on the button

            Toast.makeText(this@MainActivity, "You clicked me.", Toast.LENGTH_SHORT).show()
        }


        ipInput.addTextChangedListener(object : TextWatcher {
            override fun onTextChanged(s: CharSequence, start: Int, before: Int, count: Int) {}
            override fun beforeTextChanged(s: CharSequence, start: Int, count: Int, after: Int) {}
            override fun afterTextChanged(s: Editable) {
                if (isNumericAddress(s.toString())){
                    Toast.makeText(this@MainActivity, "Correct", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@MainActivity, "Wrong", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
}