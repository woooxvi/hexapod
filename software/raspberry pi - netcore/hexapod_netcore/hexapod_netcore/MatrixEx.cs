using MathNet.Numerics.LinearAlgebra.Double;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore
{
    public static class MatrixEx
    {
        public static Matrix Roll(this Matrix a, int shift, int axis = 0)
        {
            if (axis != 0) throw new Exception();
            shift = shift % a.RowCount;
            var res = new DenseMatrix(a.RowCount, a.ColumnCount);
            res.SetSubMatrix(0, 0, a.SubMatrix(a.RowCount - shift, shift, 0, a.ColumnCount));
            res.SetSubMatrix(shift, 0, a.SubMatrix(0, a.RowCount - shift, 0, a.ColumnCount));
            return res;
        }

        public static Matrix Flip(this Matrix a, int axis = 0)
        {
            if (axis != 0) throw new Exception();

            var res = DenseMatrix.Create(a.RowCount, a.ColumnCount, (r, c) => a[a.RowCount - 1 - r, c]);
            return res;
        }

        public static double[,] GetPart(this double[,,] a, int idx)
        {
            var res = new double[a.GetLength(1), a.GetLength(2)];
            for (int i = 0; i < res.GetLength(0); i++)
            {
                for (int j = 0; j < res.GetLength(1); j++)
                {
                    res[i, j] = a[idx, i, j];
                }
            }
            return res;
        }

        public static double[] GetPart(this double[,] a, int idx)
        {
            var res = new double[a.GetLength(1)];
            for (int i = 0; i < res.GetLength(0); i++)
            {
                res[i] = a[idx, i];
            }
            return res;
        }
    }
}
