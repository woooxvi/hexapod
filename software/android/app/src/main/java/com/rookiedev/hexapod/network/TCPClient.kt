package com.rookiedev.hexapod.network

import com.rookiedev.hexapod.ControlActivity
import java.io.*
import java.net.*


class TCPClient(
    ip: String?,
    port: Int,
    messagelistener: OnMessageReceived?,
    onconnected: OnConnectEstablished?,
    ondisconnect: OnDisconnected?
) :
    Thread() {
    private var TCPSocket: Socket? = null
    private var SERVERIP: InetAddress? = null
    private val SERVERPORT: Int
    private var serverAddr: InetSocketAddress? = null
    private var TCPOut: PrintWriter? = null
    private var TCPIn: BufferedReader? = null
    private var mMessageListener: OnMessageReceived? = null
    private var onConnected: OnConnectEstablished? = null
    private var onDisconnected: OnDisconnected? = null
    private var isConnected = false
    private var pause = false // if the thread is paused by system
    override fun run() {
        try {
            this.TCPSocket = Socket()
            this.TCPSocket!!.soTimeout = 3000
            this.TCPSocket!!.connect(serverAddr, 3000) // connecting socket and set timeout in 3s
            onConnected!!.onConnected()
            TCPOut = PrintWriter(
                BufferedWriter(OutputStreamWriter(this.TCPSocket!!.getOutputStream())),
                true
            )
            TCPIn = BufferedReader(InputStreamReader(this.TCPSocket!!.getInputStream()))
//            sendMessage("test")
            isConnected = true
            while (isConnected) {
                sleep(1000)
            }
        } catch (e: InterruptedException) {
//            controller.cancelProgressDialog(java.lang.ModuleLayer.Controller.SERVERALERT)
            println(e)
//            controller.alertDialog(0)
//            onDisconnected!!.onDisconnected()
        } catch (e: SocketTimeoutException) {
            println(e)
            onDisconnected!!.onDisconnected()
        }
    }

    /**
     * Sends the message entered by client to the server
     *
     * @param message text entered by client
     */
    fun sendMessage(message: String?) {
//        newMessage = message
//        isNewData = true

        if (this.TCPOut != null && !this.TCPOut!!.checkError()) {
            println("send message")
            this.TCPOut!!.println(message)
            this.TCPOut!!.flush()
        }
    }

    fun stopClient() {
//        sendMessage(Constants.requestMessage(Constants.REQUEST_DISCONNECT))
        pause = true
        isConnected = false
        this.TCPSocket!!.close()
    }

    interface OnMessageReceived {
        fun messageReceived(message: String?)
    }

    interface OnConnectEstablished {
        fun onConnected()
    }

    interface OnDisconnected {
        fun onDisconnected()
    }

    init {
        SERVERPORT = port
        mMessageListener = messagelistener
        onConnected = onconnected
        onDisconnected = ondisconnect
        try {
            SERVERIP = InetAddress.getByName(ip)
            serverAddr = InetSocketAddress(SERVERIP, SERVERPORT)
        } catch (e: UnknownHostException) {
            // TODO Auto-generated catch block
            e.printStackTrace()
        }
        pause = false
    }

}