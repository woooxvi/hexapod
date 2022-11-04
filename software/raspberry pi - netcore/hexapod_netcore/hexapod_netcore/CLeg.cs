using Iot.Device.ServoMotor;
using System;
using System.Collections.Generic;
using System.Data;
using System.Device.Pwm;
using System.Linq;
using System.Reflection.Metadata;
using System.Text;
using System.Threading.Tasks;
using UnitsNet;
using static hexapod_netcore.ServoKit;

namespace hexapod_netcore
{
    internal class CLeg
    {
        private readonly int id;
        private readonly MotorWarpBase[] junction_Servos;
        internal double[] correction;
        private double[] scale;
        private double[,] constraint;

        public CLeg(int id, MotorWarpBase[] junction_servos, double[] correction = null, double[] scale = null, double[,] constraint = null)
        {
            this.id = id;

            this.junction_Servos = junction_servos;

            if (correction == null) correction = new double[] { 0, 0, 0 };
            this.correction = correction;

            if (scale == null) scale = new double[] { 1, 1, 1 };
            this.scale = scale;

            if (constraint == null) constraint = new double[,] {
                { 35, 145 },
                { 0, 165 },
                { 30, 150 },
            };
            this.constraint = constraint;
        }

        internal void move_junctions(double[] angles)
        {
            this.set_angle(0, angles[0]);
            this.set_angle(1, angles[1]);
            this.set_angle(2, angles[2]);
        }

        internal void reset(bool calibrated = false)
        {
            if (calibrated)
            {
                this.set_angle(0, 90);
                this.set_angle(1, 90);
                this.set_angle(2, 90);
            }
            else
            {
                this.set_raw_angle(0, 90);
                this.set_raw_angle(1, 90);
                this.set_raw_angle(2, 90);
            }
        }

        public void set_raw_angle(int junction, double angle)
        {
            this.junction_Servos[junction].WriteAngle(angle);
        }

        public void set_offset_angle(int junction, double offsetAngle)
        {
            var target = this.junction_Servos[junction].PrevAngle + offsetAngle;
            this.junction_Servos[junction].WriteAngle(target);
        }

        public void set_angle(int junction, double angle)
        {
            var set_angle = new double[]
            {
                angle + this.correction[junction],
                this.constraint[junction,1] + this.correction[junction],
                180
            }.Min();

            set_angle = new double[] {
                set_angle,
                this.constraint[junction,0] + this.correction[junction],
                0}.Max();
            this.junction_Servos[junction].WriteAngle(set_angle);
        }
    }
}
