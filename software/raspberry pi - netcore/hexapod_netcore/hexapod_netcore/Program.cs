// See https://aka.ms/new-console-template for more information
using hexapod_netcore;
using Microsoft.Extensions.DependencyInjection;
using System.Collections.Concurrent;

var services = new List<Task>();
var cmd_queue = new ConcurrentQueue<string>();
var core = new Core(cmd_queue);
services.Add(core.Start());
var tcpServer = new TCPServer(cmd_queue, core.config.IPAddr, core.config.IPPort);
services.Add(tcpServer.Start());

Console.CancelKeyPress += (s, e) =>
{
    core.Stop();
    tcpServer.Stop();
};

Task.WaitAll(services.ToArray());
