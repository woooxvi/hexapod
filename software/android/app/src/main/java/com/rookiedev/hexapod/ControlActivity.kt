package com.rookiedev.hexapod

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.DialogInterface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.*
import android.widget.Button
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import com.rookiedev.hexapod.network.BluetoothClient
import com.rookiedev.hexapod.network.TCPClient
import kotlinx.coroutines.*
import kotlin.math.PI
import kotlin.math.atan2
import kotlin.math.pow
import kotlin.math.sqrt


/**
 * Behaviors of immersive mode.
 */
enum class BehaviorOption(
    val title: String,
    val value: Int
) {
    // Swipe from the edge to show a hidden bar. Gesture navigation works regardless of visibility
    // of the navigation bar.
    Default(
        "BEHAVIOR_DEFAULT",
        WindowInsetsController.BEHAVIOR_DEFAULT
    ),

    // "Sticky immersive mode". Swipe from the edge to temporarily reveal the hidden bar.
    ShowTransientBarsBySwipe(
        "BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE",
        WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
    )
}

/**
 * Type of system bars to hide or show.
 */
enum class TypeOption(
    val title: String,
    val value: Int
) {
    // Both the status bar and the navigation bar
    SystemBars(
        "systemBars()",
        WindowInsets.Type.systemBars()
    ),

    // The status bar only.
    StatusBar(
        "statusBars()",
        WindowInsets.Type.statusBars()
    ),

    // The navigation bar only
    NavigationBar(
        "navigationBars()",
        WindowInsets.Type.navigationBars()
    )
}

class ControlActivity : AppCompatActivity() {
    companion object {
        private const val CMD_STANDBY = "standby:"
        private const val CMD_LAYDOWN = "laydown:"

        private const val CMD_FORWARD = "forward:"
        private const val CMD_BACKWARD = "backward:"

        private const val CMD_FASTFORWARD = "fastforward:"
        private const val CMD_FASTBACKWARD = "fastbackward:"

        private const val CMD_SHIFTLEFT = "shiftleft:"
        private const val CMD_SHIFTRIGHT = "shiftright:"

        private const val CMD_TURNLEFT = "turnleft:"
        private const val CMD_TURNRIGHT = "turnright:"

        private const val CMD_CLIMBFORWARD = "climbforward:"
        private const val CMD_CLIMBBACKWARD = "climbbackward:"

        private const val CMD_ROTATEX = "rotatex:"
        private const val CMD_ROTATEY = "rotatey:"
        private const val CMD_ROTATEZ = "rotatez:"

        private const val CMD_TWIST = "twist:"
    }
    private var width = 0
    private var height = 0
    private var radius = 0f

    private var connectInterface: String = ""

    private var mContext: Context? = null

    private var tcpClient: TCPClient? = null
    private var ip: String = ""
    private var port = 0

    private var btClient: BluetoothClient? = null
    private var mac: String = ""

    private val scope = CoroutineScope(Job() + Dispatchers.IO)

    private var currentState: String = CMD_STANDBY
    private lateinit var progressBar: ConstraintLayout

    private var controlImage: ImageView? = null

    private var buttonRotateX: Button? = null
    private var buttonRotateY: Button? = null
    private var buttonRotateZ: Button? = null
    private var buttonClimb: Button? = null
    private var buttonTwist: Button? = null


    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_control)

        val myIntent = intent // gets the previously created intent

        mContext = applicationContext

        connectInterface = myIntent.getStringExtra("interface").toString()
        if (connectInterface == "WiFi") {
            ip = myIntent.getStringExtra("ip").toString()
            port = myIntent.getStringExtra("port").toString().toInt()
        } else if (connectInterface == "Bluetooth") {
            mac = myIntent.getStringExtra("mac").toString()
        }

        controlWindowInsets(true)

        controlImage = findViewById<ImageView>(R.id.control_image)
        progressBar = findViewById<ConstraintLayout>(R.id.progressBar)

        buttonRotateX = findViewById(R.id.button_rotatex)
        buttonRotateY = findViewById(R.id.button_rotatey)
        buttonRotateZ = findViewById(R.id.button_rotatez)
        buttonClimb = findViewById(R.id.button_climb)
        buttonTwist = findViewById(R.id.button_twist)

        val vto: ViewTreeObserver = controlImage!!.viewTreeObserver
        vto.addOnPreDrawListener(object : ViewTreeObserver.OnPreDrawListener {
            override fun onPreDraw(): Boolean {
                controlImage!!.viewTreeObserver.removeOnPreDrawListener(this)
                height = controlImage!!.measuredHeight
                width = controlImage!!.measuredWidth
                radius = width.coerceAtMost(height) / 2f
                return true
            }
        })

        controlImage!!.setOnTouchListener(
            object : View.OnTouchListener {
                override fun onTouch(view: View, motionEvent: MotionEvent): Boolean {
                    val touchX = motionEvent.x
                    val touchY = motionEvent.y
                    if (touchX < 0) {
                        return false
                    }
                    if (touchY < 0) {
                        return false
                    }

                    val coorX = touchX - width / 2
                    val coorY = touchY - height / 2

                    val length = sqrt(coorX.pow(2) + coorY.pow(2))
                    if (length < radius / 3) {
                        if (currentState != CMD_STANDBY) {
                            sendMessageAsync(CMD_STANDBY)
                            currentState = CMD_STANDBY
                            controlImage!!.setImageResource(R.drawable.ic_control_circle_standby)

                            buttonRotateX!!.backgroundTintList =
                                applicationContext.getColorStateList(R.color.grey_500)
                            buttonRotateY!!.backgroundTintList =
                                applicationContext.getColorStateList(R.color.grey_500)
                            buttonRotateZ!!.backgroundTintList =
                                applicationContext.getColorStateList(R.color.grey_500)
                            buttonClimb!!.backgroundTintList =
                                applicationContext.getColorStateList(R.color.grey_500)
                            buttonTwist!!.backgroundTintList =
                                applicationContext.getColorStateList(R.color.grey_500)
                        }
                    } else if (length >= radius / 3 && length < 2 * radius / 3) {
                        val angle = atan2(coorY, coorX)
                        if (angle > -PI / 4 && angle <= PI / 4) {
                            if (currentState != CMD_SHIFTRIGHT) {
                                sendMessageAsync(CMD_SHIFTRIGHT)
                                currentState = CMD_SHIFTRIGHT
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_right)
                            }
                        } else if (angle > PI / 4 && angle <= 3 * PI / 4) {
                            if (currentState != CMD_BACKWARD) {
                                sendMessageAsync(CMD_BACKWARD)
                                currentState = CMD_BACKWARD
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_backward)
                            }
                        } else if (angle > -3 * PI / 4 && angle < -PI / 4) {
                            if (currentState != CMD_FORWARD) {
                                sendMessageAsync(CMD_FORWARD)
                                currentState = CMD_FORWARD
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_forward)
                            }
                        } else {
                            if (currentState != CMD_SHIFTLEFT) {
                                sendMessageAsync(CMD_SHIFTLEFT)
                                currentState = CMD_SHIFTLEFT
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_left)
                            }
                        }
                        buttonRotateX!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonRotateY!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonRotateZ!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonClimb!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonTwist!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                    } else if (length >= 2 * radius / 3 && length < radius) {
                        val angle = atan2(coorY, coorX)
                        if (angle > -PI / 4 && angle <= PI / 4) {
                            if (currentState != CMD_TURNRIGHT) {
                                sendMessageAsync(CMD_TURNRIGHT)
                                currentState = CMD_TURNRIGHT
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_turnright)
                            }
                        } else if (angle > PI / 4 && angle <= 3 * PI / 4) {
                            if (currentState != CMD_FASTBACKWARD) {
                                sendMessageAsync(CMD_FASTBACKWARD)
                                currentState = CMD_FASTBACKWARD
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_fastbackward)
                            }
                        } else if (angle > -3 * PI / 4 && angle < -PI / 4) {
                            if (currentState != CMD_FASTFORWARD) {
                                sendMessageAsync(CMD_FASTFORWARD)
                                currentState = CMD_FASTFORWARD
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_fastforward)
                            }
                        } else {
                            if (currentState != CMD_TURNLEFT) {
                                sendMessageAsync(CMD_TURNLEFT)
                                currentState = CMD_TURNLEFT
                                controlImage!!.setImageResource(R.drawable.ic_control_circle_turnleft)
                            }
                        }
                        buttonRotateX!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonRotateY!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonRotateZ!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonClimb!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                        buttonTwist!!.backgroundTintList =
                            applicationContext.getColorStateList(R.color.grey_500)
                    }
                    return true
                }
            }
        )

        buttonRotateX!!.setOnClickListener {
            if (currentState != CMD_ROTATEX) {
                sendMessageAsync(CMD_ROTATEX)
                currentState = CMD_ROTATEX
                controlImage!!.setImageResource(R.drawable.ic_control_circle)
                buttonRotateX!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.purple_500)
                buttonRotateY!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateZ!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonClimb!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonTwist!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
            }
        }

        buttonRotateY!!.setOnClickListener {
            if (currentState != CMD_ROTATEY) {
                sendMessageAsync(CMD_ROTATEY)
                currentState = CMD_ROTATEY
                controlImage!!.setImageResource(R.drawable.ic_control_circle)
                buttonRotateX!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateY!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.purple_500)
                buttonRotateZ!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonClimb!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonTwist!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
            }
        }

        buttonRotateZ!!.setOnClickListener {
            if (currentState != CMD_ROTATEZ) {
                sendMessageAsync(CMD_ROTATEZ)
                currentState = CMD_ROTATEZ
                controlImage!!.setImageResource(R.drawable.ic_control_circle)
                buttonRotateX!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateY!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateZ!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.purple_500)
                buttonClimb!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonTwist!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
            }
        }

        buttonClimb!!.setOnClickListener {
            if (currentState != CMD_CLIMBFORWARD) {
                sendMessageAsync(CMD_CLIMBFORWARD)
                currentState = CMD_CLIMBFORWARD
                controlImage!!.setImageResource(R.drawable.ic_control_circle)
                buttonRotateX!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateY!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateZ!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonClimb!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.purple_500)
                buttonTwist!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
            }
        }

        buttonTwist!!.setOnClickListener {
            if (currentState != CMD_TWIST) {
                sendMessageAsync(CMD_TWIST)
                currentState = CMD_TWIST
                controlImage!!.setImageResource(R.drawable.ic_control_circle)
                buttonRotateX!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateY!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonRotateZ!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonClimb!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.grey_500)
                buttonTwist!!.backgroundTintList =
                    applicationContext.getColorStateList(R.color.purple_500)
            }
        }
    }

    @SuppressLint("MissingPermission")
    override fun onResume() {
        super.onResume()
        progressBar.visibility = View.VISIBLE

        if (connectInterface == "WiFi") {
            this.tcpClient = TCPClient(ip, port, object : TCPClient.OnMessageReceived {
                override fun messageReceived(message: String?) {
                    if (message == null) {
//                    alertDialog(DISCONNECTED)
                        println("no message")
                    }
                }
            }, object : TCPClient.OnConnectEstablished {
                override fun onConnected() {
//                udpClient.start()
                    println("connected")
                    Handler(Looper.getMainLooper()).post {
                        progressBar.visibility = View.GONE
                    }
                }
            }, object : TCPClient.OnDisconnected {
                override fun onDisconnected() {
                    Handler(Looper.getMainLooper()).post {
                        progressBar.visibility = View.GONE
                        alertDialog(0)
                    }
                }
            }
            )
            this.tcpClient!!.start()
        } else if (connectInterface == "Bluetooth") {
            println("Bluetooth")
            this.btClient = BluetoothClient(mContext, mac, object : BluetoothClient.OnMessageReceived {
                override fun messageReceived(message: String?) {
                    if (message == null) {
//                    alertDialog(DISCONNECTED)
                        println("no message")
                    }
                }
            }, object : BluetoothClient.OnConnectEstablished {
                override fun onConnected() {
//                udpClient.start()
                    println("connected")
                    Handler(Looper.getMainLooper()).post {
                        progressBar.visibility = View.GONE
                    }
                }
            }, object : BluetoothClient.OnDisconnected {
                override fun onDisconnected() {
                    Handler(Looper.getMainLooper()).post {
                        progressBar.visibility = View.GONE
                        alertDialog(0)
                    }
                }
            }
            )
            this.btClient!!.start()

        }

        currentState = CMD_STANDBY
        controlImage!!.setImageResource(R.drawable.ic_control_circle_standby)

        buttonRotateX!!.backgroundTintList =
            applicationContext.getColorStateList(R.color.grey_500)
        buttonRotateY!!.backgroundTintList =
            applicationContext.getColorStateList(R.color.grey_500)
        buttonRotateZ!!.backgroundTintList =
            applicationContext.getColorStateList(R.color.grey_500)
        buttonClimb!!.backgroundTintList =
            applicationContext.getColorStateList(R.color.grey_500)
        buttonTwist!!.backgroundTintList =
            applicationContext.getColorStateList(R.color.grey_500)

    }

    override fun onPause() {
        super.onPause()
        println("on Pause")

//        saveSharedPref()
        if (connectInterface == "WiFi") {
            tcpClient!!.stopClient()
            tcpClient!!.interrupt()
        }else if (connectInterface == "Bluetooth"){
            btClient!!.stopClient()
            btClient!!.interrupt()
        }

    }


    private fun controlWindowInsets(hide: Boolean) {
        // WindowInsetsController can hide or show specified system bars.
        val insetsController = window.decorView.windowInsetsController ?: return
        // The behavior of the immersive mode.
        val behavior = BehaviorOption.values()[1].value
        // The type of system bars to hide or show.
        val type = TypeOption.values()[0].value
        insetsController.systemBarsBehavior = behavior
        if (hide) {
            insetsController.hide(type)
        } else {
            insetsController.show(type)
        }
    }

    fun sendMessageAsync(message: String) {
        // Starts a new coroutine within the scope
        scope.launch {
            // New coroutine that can call suspend functions

            withContext(Dispatchers.IO) {              // Dispatchers.IO (main-safety block)
                if (connectInterface == "WiFi") {
                    tcpClient?.sendMessage(message)
                }else if(connectInterface == "Bluetooth"){
                    btClient?.sendMessage(message)
                }
            }
        }
    }

    fun alertDialog(type: Int) {
        val alert: AlertDialog = AlertDialog.Builder(this).create()
        when (type) {
            0 -> {
                alert.setTitle("Error")
                alert.setIcon(R.drawable.ic_baseline_error_24)
                alert.setMessage(
                    "Unable to connect to the Hexapod."
                )
                alert.setOnCancelListener(DialogInterface.OnCancelListener { finish() })
                alert.setButton(AlertDialog.BUTTON_POSITIVE,
                    "OK",
                    DialogInterface.OnClickListener { dialog, which -> finish() })
            }
        }
        alert.show()
    }
}


