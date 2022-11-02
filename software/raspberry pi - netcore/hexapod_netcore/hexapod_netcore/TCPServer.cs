using MathNet.Numerics;
using SixLabors.ImageSharp.Advanced;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore
{
    public class TCPServer
    {
        private readonly ConcurrentQueue<string> cmd_queue;
        private readonly string iPAddr;
        private readonly int iPPort;
        private TcpListener tcp_socket;
        private object monitor;
        private bool running;

        public Thread threadCore { get; set; }

        public TCPServer(ConcurrentQueue<string> out_cmd_queue, string iPAddr, int iPPort)
        {
            cmd_queue = out_cmd_queue;
            this.iPAddr = iPAddr;
            this.iPPort = iPPort;
        }

        public TCPServer(ConcurrentQueue<string> out_cmd_queue, string iPAddr, int iPPort, object monitor) : this(out_cmd_queue, iPAddr, iPPort)
        {
            this.monitor = monitor;
        }

        public Task Start()
        {
            this.running = true;
            return Task.Run(core);
        }

        private void core()
        {
            try
            {

                // Buffer for reading data
                Byte[] bytes = new Byte[256];
                String data = null;

                this.tcp_socket = new TcpListener(IPAddress.Parse(iPAddr), iPPort);
                this.tcp_socket.Start(1);

                // Enter the listening loop.
                while (running)
                {

                    Console.Write("Waiting for a connection... ");
                    TcpClient client = null;
                    try
                    {
                        client = tcp_socket.AcceptTcpClientAsync().Result;
                        Console.WriteLine("Connected!");

                        data = null;

                        // Get a stream object for reading and writing
                        NetworkStream stream = client.GetStream();

                        int i;

                        // Loop to receive all the data sent by the client.
                        while ((i = stream.Read(bytes, 0, bytes.Length)) != 0)
                        {
                            data = System.Text.Encoding.UTF8.GetString(bytes, 0, i);
                            Console.WriteLine("Received: {0}", data);

                            this.cmd_queue.Enqueue(data);

                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("ClientException: {0}", ex);
                        // Shutdown and end connection
                        client?.Close();
                    }
                }
            }
            catch (SocketException e)
            {
                Console.WriteLine("SocketException: {0}", e);
            }
            finally
            {
                // Stop listening for new clients.
                tcp_socket.Stop();
                this.cmd_queue.Enqueue("standby:");
                Console.WriteLine("tcp closed!");
            }
        }

        public void Stop()
        {
            this.running = false;
        }
    }
}
