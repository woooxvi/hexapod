package com.rookiedev.hexapod.network

import com.rookiedev.hexapod.ControlActivity
import android.util.Log
import java.io.*
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Socket
import java.net.UnknownHostException
import java.util.concurrent.locks.ReentrantLock


class TCPClient(
    c: ControlActivity,
    ip: String?,
    port: Int,
    messagelistener: OnMessageReceived?,
    onconnected: OnConnectEstablished?,
    ondisconnect: OnDisconnected?
) :
    Thread() {
    private val controller: ControlActivity = c
    private var TCPSocket:Socket? = null
    private var SERVERIP: InetAddress? = null
    private val SERVERPORT: Int
    private var serverAddr: InetSocketAddress? = null
    private var TCPOut: PrintWriter? = null
    private var TCPIn: BufferedReader? = null
    private var TCPMessage: String? = null
    private var mMessageListener: OnMessageReceived? = null
    private var onConnected: OnConnectEstablished? = null
    private var onDisconnected: OnDisconnected?=null
    private var isConnected = false
    private var pause = false // if the thread is paused by system
    private var isNewData = false
    private var newMessage:String? = null
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
//            sendMessage("test")
            isConnected = true
            while(isConnected)
            {
//                if (isNewData)
//                {
//                    if (TCPOut != null && !TCPOut!!.checkError()) {
//                        TCPOut!!.println(newMessage)
//                        TCPOut!!.flush()
//                    }
//                    isNewData = false
//                }else{
//                    sleep(100)
//                }
                sleep(1000)
            }
        } catch (e: Exception) {
//            controller.cancelProgressDialog(java.lang.ModuleLayer.Controller.SERVERALERT)
            println("unable to connect")
//            controller.alertDialog(0)
            onDisconnected!!.onDisconnected()
        }
    }

//    private fun keepAlive() {
//        sendMessage(Constants.requestMessage(Constants.REQUEST_ISALIVE))
//        try {
//            TCPMessage = TCPIn!!.readLine()
//            mMessageListener!!.messageReceived(TCPMessage)
//        } catch (e: IOException) {
//            controller.alertDialog(java.lang.ModuleLayer.Controller.DISCONNECTED)
//        }
//    }

    /**
     * Sends the message entered by client to the server
     *
     * @param message text entered by client
     */
    fun sendMessage(message: String?) {
//        newMessage = message
//        isNewData = true
        if (TCPOut != null && !TCPOut!!.checkError()) {
            TCPOut!!.println(message)
            TCPOut!!.flush()
        }
    }

//    fun stopClient() {
//        sendMessage(Constants.requestMessage(Constants.REQUEST_DISCONNECT))
//        pause = true
//        isConnected = false
//    }

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