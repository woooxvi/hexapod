using SixLabors.ImageSharp.Advanced;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore.Model
{
    public class CConfig
    {
        public string[] legNames { get; set; }
        public double[] legMountX { get; set; }
        public double[] legMountY { get; set; }
        public double[] legMountAngle { get; set; }
        public double legRootToJoint1 { get; set; }
        public double legJoint1ToJoint2 { get; set; }
        public double legJoint2ToJoint3 { get; set; }
        public double legJoint3ToTip { get; set; }
        public int movementInterval { get; set; }
        public int movementSwitchDuration { get; set; }
        public double[] leg0Offset { get; set; }
        public double[] leg0Scale { get; set; }
        public double[] leg1Offset { get; set; }
        public double[] leg1Scale { get; set; }
        public double[] leg2Offset { get; set; }
        public double[] leg2Scale { get; set; }
        public double[] leg3Offset { get; set; }
        public double[] leg3Scale { get; set; }
        public double[] leg4Offset { get; set; }
        public double[] leg4Scale { get; set; }
        public double[] leg5Offset { get; set; }
        public double[] leg5Scale { get; set; }
        public string IPAddr { get; set; }
        public int IPPort { get; set; }

        public void SetOffset(int legIdx, double[] value)
        {
            switch (legIdx)
            {
                case 0: this.leg0Offset = value; break;
                case 1: this.leg1Offset = value; break;
                case 2: this.leg2Offset = value; break;
                case 3: this.leg3Offset = value; break;
                case 4: this.leg4Offset = value; break;
                case 5: this.leg5Offset = value; break;
                default: throw new Exception("!!");
            }
        }
    }
}
