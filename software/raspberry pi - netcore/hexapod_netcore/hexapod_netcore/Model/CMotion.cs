using MathNet.Numerics.LinearAlgebra.Double;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore.Model
{
    public class CMotion : CAction
    {
        public CMotion(double[,,] coord)
        {
            this.coord = coord;
        }

        public double[,,] coord { get; internal set; }
    }
}
