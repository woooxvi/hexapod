using Iot.Device.Pwm;
using Iot.Device.ServoMotor;
using System;
using System.Collections.Generic;
using System.Device.I2c;
using System.Device.Pwm;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore
{
    public class ServoKit
    {
        private Pca9685 pca;
        private List<IMotorWarp> servos;

        public ServoKit(int channels, int address, bool forceSimulator = false)
        {
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows) == false && forceSimulator != true)
            {
                this.pca = new Pca9685(I2cDevice.Create(new I2cConnectionSettings(address, Pca9685.I2cAddressBase)));
                this.servos = new List<IMotorWarp>();
                for (int i = 0; i < channels; i++)
                {
                    var servo = new ServoMotor(this.pca.CreatePwmChannel(i), 180, 500, 2500);
                    servo.Start();
                    servos.Add(new ServoMotorTruth(servo));
                }
            }
            else
            {
                this.pca = null;
                this.servos = new List<IMotorWarp>();
                for (int i = 0; i < channels; i++)
                {
                    servos.Add(new ServoMotorSimulator(address, i));
                }
            }
        }

        internal IMotorWarp[] Take(params int[] indexs)
        {
            return servos.Where((channel, index) => indexs.Contains(index)).ToArray();
        }

        public class ServoMotorSimulator : IMotorWarp
        {
            public ServoMotorSimulator(int address, int channel)
            {
                Address = address;
                Channel = channel;
            }

            public int Address { get; }
            public int Channel { get; }
            public double prevAngle { get; set; }

            public void WriteAngle(double angle)
            {
                if (prevAngle.Equals(angle) == false)
                {
                    Console.WriteLine($"{Address}-{Channel}设置为{angle}°");
                    prevAngle = angle;
                }
            }
        }

        public class ServoMotorTruth : IMotorWarp
        {
            public ServoMotorTruth(ServoMotor motor)
            {
                Motor = motor;
            }

            public ServoMotor Motor { get; set; }
            public void WriteAngle(double angle)
            {
                Motor.WriteAngle(angle);
            }

        }

        public interface IMotorWarp
        {
            void WriteAngle(double angle);
        }
    }

}
