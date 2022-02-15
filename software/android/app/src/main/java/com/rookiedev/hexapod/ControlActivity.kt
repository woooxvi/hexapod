package com.rookiedev.hexapod

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.*
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import com.rookiedev.hexapod.network.TCPClient
import com.rookiedev.hexapod.network.TCPClient.OnConnectEstablished
import com.rookiedev.hexapod.network.TCPClient.OnMessageReceived
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
    private var pxMargin = 0f
    private var width = 0
    private var height = 0
    private var radius = 0f

    private var tcpClient: TCPClient? = null
    private var ip:String = ""
    private var port = 0

    private val scope = CoroutineScope(Job() + Dispatchers.IO)

    private var currentState: String = "standby"


    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_control)

        val myIntent = intent // gets the previously created intent

        ip = myIntent.getStringExtra("ip").toString()
        port = myIntent.getStringExtra("port").toString().toInt()

        controlWindowInsets(true)

        val controlCircle = findViewById<ImageView>(R.id.control_image)

        val vto: ViewTreeObserver = controlCircle.viewTreeObserver
        vto.addOnPreDrawListener(object : ViewTreeObserver.OnPreDrawListener {
            override fun onPreDraw(): Boolean {
                controlCircle.viewTreeObserver.removeOnPreDrawListener(this)
                height = controlCircle.measuredHeight
                width = controlCircle.measuredWidth
                radius = width.coerceAtMost(height) / 2f
                println(radius)
                return true
            }
        })

        controlCircle.setOnTouchListener(
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
                        if (currentState != "standby") {
                            println("Standby")
                            sendMessageAsync("standby")
                            currentState = "standby"
                        }
                    } else if (length >= radius / 3 && length < 2 * radius / 3) {
                        val angle = atan2(coorY, coorX)
                        if (angle > -PI / 4 && angle <= PI / 4) {
                            if (currentState != "shiftright") {
                                println("Move right")
                                sendMessageAsync("shiftright")
                                currentState = "shiftright"
                            }
                        } else if (angle > PI / 4 && angle <= 3 * PI / 4) {
                            if (currentState != "backward") {
                                println("Move back")
                                sendMessageAsync("backward")
                                currentState = "backward"
                            }
                        } else if (angle > -3 * PI / 4 && angle < -PI / 4) {
                            if (currentState != "forward") {
                                println("Move forward")
                                sendMessageAsync("forward")
                                currentState = "forward"
                            }
                        } else {
                            if (currentState != "shiftleft") {
                                println("Move left")
                                sendMessageAsync("shiftleft")
                                currentState = "shiftleft"
                            }
                        }
                    } else if (length >= 2 * radius / 3 && length < radius) {
                        val angle = atan2(coorY, coorX)
                        if (angle > -PI / 4 && angle <= PI / 4) {
                            if (currentState != "rightturn") {
                                println("Turn right")
                                sendMessageAsync("rightturn")
                                currentState = "rightturn"
                            }
                        } else if (angle > PI / 4 && angle <= 3 * PI / 4) {
                            if (currentState != "fastback") {
                                println("Fast back")
//                            sendMessageAsync("Fast back")
                                currentState = "fastback"
                            }
                        } else if (angle > -3 * PI / 4 && angle < -PI / 4) {
                            if (currentState != "fastforward") {
                                println("Fast forward")
                                sendMessageAsync("fastforward")
                                currentState = "fastforward"
                            }
                        } else {
                            if (currentState != "leftturn") {
                                println("Turn left")
                                sendMessageAsync("leftturn")
                                currentState = "leftturn"
                            }
                        }
                    }
                    return true
                }
            }
        )
        this.tcpClient = TCPClient(this, ip, port, object : OnMessageReceived {
            override fun messageReceived(message: String?) {
                if (message == null) {
//                    alertDialog(DISCONNECTED)
                    println("no message")
                }
            }
        }, object : OnConnectEstablished {
            override fun onConnected() {
//                udpClient.start()
                println("connected")
            }
        }
        )
        this.tcpClient!!.start()
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
                tcpClient?.sendMessage(message)
            }
        }
    }
}


