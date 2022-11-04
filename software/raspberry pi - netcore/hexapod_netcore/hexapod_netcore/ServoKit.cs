using Iot.Device.Mcp25xxx.Register;
using Iot.Device.Pwm;
using Iot.Device.ServoMotor;
using System;
using System.Collections.Generic;
using System.Device.I2c;
using System.Device.Pwm;
using System.Diagnostics;
using System.Drawing.Printing;
using System.Linq;
using System.Reflection.Metadata;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using UnitsNet;

namespace hexapod_netcore
{
    public class ServoKit
    {
        private Pca9685 pca;
        private List<MotorWarpBase> servos;
        public const int MILLISECOND_COST_PER_60 = 120;
        public const int MILLISECOND_COST_MIN = 20;

        public ServoKit(int channels, int i2cIdx, int address = Pca9685.I2cAddressBase, bool forceSimulator = false)
        {
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows) == false && forceSimulator != true)
            {
                this.pca = new Pca9685(I2cDevice.Create(new I2cConnectionSettings(i2cIdx, address)));
                this.servos = new List<MotorWarpBase>();
                for (int i = 0; i < channels; i++)
                {
                    var servo = new ServoMotor(this.pca.CreatePwmChannel(i), 180, 500, 2500);
                    servo.Start();
                    servos.Add(new ServoMotorTruth(servo, i2cIdx, address, i));
                }
            }
            else
            {
                this.pca = null;
                this.servos = new List<MotorWarpBase>();
                for (int i = 0; i < channels; i++)
                {
                    servos.Add(new ServoMotorSimulator(i2cIdx, address, i));
                }
            }
        }

        internal MotorWarpBase[] Take(params int[] indexs)
        {
            return indexs.Select(idx => servos[idx]).ToArray();
            //return servos.Where((channel, index) => indexs.Contains(index)).ToArray();
        }

        public class ServoMotorSimulator : MotorWarpBase
        {
            public ServoMotorSimulator(int i2cIdx, int address, int channel) : base(i2cIdx, address, channel)
            {

            }
        }

        public class ServoMotorTruth : MotorWarpBase
        {
            public ServoMotorTruth(ServoMotor motor, int i2cIdx, int address, int channel) : base(i2cIdx, address, channel)
            {
                Motor = motor;
            }

            public ServoMotor Motor { get; set; }
            protected override void writeAngle(double angle)
            {
                Motor.WriteAngle(angle);
            }
        }

        public abstract class MotorWarpBase : IDisposable
        {
            private double targetAngle = -1;
            public double PrevAngle { get; protected set; } = -1;

            public int I2CIdx { get; }
            public int Address { get; }
            public int Channel { get; }

            private Thread threadCore = null;
            private bool isDispose = false;
            double timeCost = 0;

            public MotorWarpBase(int i2cIdx, int address, int channel)
            {
                I2CIdx = i2cIdx;
                Address = address;
                Channel = channel;
                isDispose = false;
                threadCore = new Thread(core);
                //threadCore.Priority = ThreadPriority.BelowNormal;
                threadCore.Start();
            }

            public void Dispose()
            {
                this.isDispose = false;
            }

            public void WriteAngle(double angle)
            {
                targetAngle = angle;
            }

            protected virtual void writeAngle(double angle)
            {

            }

            private void core()
            {
                while (isDispose == false)
                {
                    if (targetAngle >= 0 && PrevAngle.Equals(targetAngle) == false)
                    {
                        //改变了
                        if (PrevAngle >= 0)
                            timeCost = (MILLISECOND_COST_PER_60 / 60.0) * Math.Abs(targetAngle - PrevAngle) * TimeSpan.TicksPerMillisecond;
                        timeCost = Math.Min(MILLISECOND_COST_MIN, timeCost);
                        long startTick = Stopwatch.GetTimestamp();
                        long targetTick = (long)(startTick + timeCost);
                        this.writeAngle(targetAngle);
                        Console.WriteLine($"{Address - Pca9685.I2cAddressBase}-{Channel}: {PrevAngle} -> {targetAngle}°");
                        PrevAngle = targetAngle;
                        while (Stopwatch.GetTimestamp() < targetTick)
                        {
                            Thread.SpinWait(1);
                        }
                    }
                }
            }
        }
    }

}
