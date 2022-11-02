using hexapod_netcore.Model;
using Iot.Device.SenseHat;
using MathNet.Numerics.LinearAlgebra.Double;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Diagnostics;
using System.Linq;
using System.Reflection.Metadata;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore
{
    public partial class Core
    {
        private object monitor;

        public Core(ConcurrentQueue<string> in_cmd_queue, object monitor) : this(in_cmd_queue)
        {
            this.monitor = monitor;
        }

        /// <summary>
        /// 测试过
        /// </summary>
        /// <param name="radius"></param>
        /// <param name="steps"></param>
        /// <param name="reverse"></param>
        /// <returns></returns>
        public Matrix semicircle_generator(double radius, int steps, bool reverse = false)
        {
            Debug.Assert(steps % 4 == 0);
            var halfsteps = Convert.ToInt32(steps / 2);
            var step_angle = Math.PI / halfsteps;
            var result = DenseMatrix.Create(steps, 3, 0);
            var halfsteps_array = DenseMatrix.Create(halfsteps, 1, (r, c) => r);
            //result.SetColumn(1, (radius - halfsteps_array * 2 / (halfsteps)).Column(0));


            result.SetSubMatrix(0, 1, radius - halfsteps_array * radius * 2 / halfsteps);

            var angle = Math.PI - step_angle * halfsteps_array;

            result.SetSubMatrix(halfsteps, 1, radius * angle.PointwiseCos());
            result.SetSubMatrix(halfsteps, 2, radius * angle.PointwiseSin());


            result = (DenseMatrix)result.Roll(Convert.ToInt32(steps / 4), axis: 0);
            if (reverse)
            {
                result = (DenseMatrix)result.Flip(axis: 0);
                result = (DenseMatrix)result.Roll(1, axis: 0);
                //Console.WriteLine("result.ToMatrixString()");
                //Console.WriteLine(result.ToMatrixString(int.MaxValue, int.MaxValue));
            }
            //Console.WriteLine("result.ToMatrixString()");
            //Console.WriteLine(result.ToMatrixString(int.MaxValue, int.MaxValue));


            //for (int i = 0; i < halfsteps; i++)
            //{
            //    result[i, 1] = radius - i * radius * 2 / halfsteps;
            //    var angle = Math.PI - step_angle * i;
            //    result[halfsteps + i, 1] = (double)(radius * Math.Cos(angle));
            //    result[halfsteps + i, 2] = (double)(radius * Math.Sin(angle));
            //}

            //result = roll(result, Convert.ToInt32(steps / 4));

            //if (reverse)
            //{
            //    flip(result);
            //    roll(result, 1);
            //}
            return result;



            #region 备份2022年10月28日
            //Debug.Assert(steps % 4 == 0);
            //var halfsteps = Convert.ToInt32(steps / 2);
            //var step_angle = Math.PI / halfsteps;
            //var result = new double[steps, 3];

            //for (int i = 0; i < halfsteps; i++)
            //{
            //    result[i, 1] = radius - i * radius * 2 / halfsteps;
            //    var angle = Math.PI - step_angle * i;
            //    result[halfsteps + i, 1] = (double)(radius * Math.Cos(angle));
            //    result[halfsteps + i, 2] = (double)(radius * Math.Sin(angle));
            //}

            //result = roll(result, Convert.ToInt32(steps / 4));

            //if (reverse)
            //{
            //    flip(result);
            //    roll(result, 1);
            //}
            //return result;

            #endregion



            //double[] halfsteps_array = new double[halfsteps];
            //// first half, move backward (only y change)
            //result[::halfsteps, 1] = radius - halfsteps_array * radius * 2 / halfsteps;
            //// second half, move forward in semicircle shape (y, z change)
            //var angle = np.pi - step_angle * halfsteps_array;
            //result[halfsteps, 1] = radius * np.cos(angle);
            //result[halfsteps, 2] = radius * np.sin(angle);
            //result = np.roll(result, Convert.ToInt32(steps / 4), axis: 0);
            //if (reverse)
            //{
            //    result = np.flip(result, axis: 0);
            //    result = np.roll(result, 1, axis: 0);
            //}
        }


        public Matrix semicircle2_generator(int steps, double y_radius, double z_radius, double x_radius, bool reverse = false)
        {
            Debug.Assert(steps % 4 == 0);
            var halfsteps = Convert.ToInt32(steps / 2);
            var step_angle = Math.PI / halfsteps;
            var result = DenseMatrix.Create(steps, 3, 0);
            var halfsteps_array = DenseMatrix.Create(halfsteps, 1, (r, c) => r);
            // first half, move backward (only y change)
            result.SetSubMatrix(0, 1, y_radius - halfsteps_array * y_radius * 2 / halfsteps);
            // second half, move forward in semicircle shape (x, y, z change)
            var angle = Math.PI - step_angle * halfsteps_array;
            result.SetSubMatrix(halfsteps, 0, x_radius * angle.PointwiseSin());

            angle = Math.PI - step_angle * halfsteps_array;
            result.SetSubMatrix(halfsteps, 1, y_radius * angle.PointwiseCos());

            angle = Math.PI - step_angle * halfsteps_array;
            result.SetSubMatrix(halfsteps, 2, z_radius * angle.PointwiseSin());

            result = (DenseMatrix)result.Roll(Convert.ToInt32(steps / 4), axis: 0);
            if (reverse)
            {
                result = (DenseMatrix)result.Flip(axis: 0);
                result = (DenseMatrix)result.Roll(1, axis: 0);
            }
            return result;
        }

        //private double[,] flip(double[,] a)
        //{
        //    var result = new double[a.GetLength(0), a.GetLength(1)];
        //    for (int i = 0; i < a.GetLength(0); i++)
        //    {
        //        for (int j = 0; j < a.GetLength(1); j++)
        //        {
        //            result[i, j] = a[a.GetLength(0) - i, j];
        //        }
        //    }
        //    return result;
        //}

        //private double[,] roll(double[,] a, int shift)
        //{
        //    var result = new double[a.GetLength(0), a.GetLength(1)];
        //    shift = shift % a.GetLength(0);
        //    for (int i = 0; i < a.GetLength(0); i++)
        //    {
        //        for (int j = 0; j < a.GetLength(1); j++)
        //        {
        //            if (i < shift)
        //            {
        //                result[i, j] = a[a.GetLength(0) - shift + i, j];
        //            }
        //            else
        //            {
        //                result[i, j] = a[i - shift, j];
        //            }
        //        }
        //    }
        //    return result;
        //}

        //public static void semicircle2_generator(
        //    object steps,
        //    object y_radius,
        //    object z_radius,
        //    object x_radius,
        //    bool reverse = false)
        //{
        //    Debug.Assert(steps % 4 == 0);
        //    var halfsteps = Convert.ToInt32(steps / 2);
        //    var step_angle = np.pi / halfsteps;
        //    var result = np.zeros((steps, 3));
        //    var halfsteps_array = np.arange(halfsteps);
        //    // first half, move backward (only y change)
        //    result[::halfsteps, 1] = y_radius - halfsteps_array * y_radius * 2 / halfsteps;
        //    // second half, move forward in semicircle shape (x, y, z change)
        //    var angle = np.pi - step_angle * halfsteps_array;
        //    result[halfsteps, 0] = x_radius * np.sin(angle);
        //    result[halfsteps, 1] = y_radius * np.cos(angle);
        //    result[halfsteps, 2] = z_radius * np.sin(angle);
        //    result = np.roll(result, Convert.ToInt32(steps / 4), axis: 0);
        //    if (reverse)
        //    {
        //        result = np.flip(result, axis: 0);
        //        result = np.roll(result, 1, axis: 0);
        //    }
        //    return result;
        //}

        public DenseMatrix get_rotate_x_matrix(double angle)
        {
            angle = angle * Math.PI / 180d;
            return DenseMatrix.OfArray(new double[,]
            {
                {1, 0,                  0,                  0 },
                {0, Math.Cos(angle),    -Math.Sin(angle),   0 },
                {0, Math.Sin(angle),    Math.Cos(angle),    0 },
                {0, 0,                  0,                  1 },
            });
        }

        public DenseMatrix get_rotate_y_matrix(double angle)
        {
            angle = (double)(angle * Math.PI / 180);
            return DenseMatrix.OfArray(new double[,]
            {
                 {Math.Cos(angle),  0,  Math.Sin(angle),    0 },
                 {0,                1,  0,                  0 },
                 {-Math.Sin(angle), 0,  Math.Cos(angle),    0 },
                 {0,                0,  0,                  1 },
            });
        }

        /// <summary>
        /// 测试过
        /// </summary>
        /// <param name="angle"></param>
        /// <returns></returns>
        public Matrix get_rotate_z_matrix(double angle)
        {
            angle = (double)(angle * Math.PI / 180);
            return DenseMatrix.OfArray(new double[,]
            {
                 {Math.Cos(angle),   -Math.Sin(angle),    0,  0 },
                 {Math.Sin(angle),   Math.Cos(angle),     0,  0 },
                 {0,                        0,            1,  0 },
                 {0,                        0,            0,  1 },
            });
        }



        //public static void matrix_mul(object m, object pt)
        //{
        //    var ptx = pt.ToList() + new List<int> {
        //    1
        //};
        //    return (m * np.matrix(ptx).T).T.flat.ToList()[:: - 1];
        //}

        //public static void path_rotate_x(object path, object angle)
        //{
        //    var ptx = np.append(path, np.ones((np.shape(path)[0], 1)), axis: 1);
        //    return (get_rotate_x_matrix(angle) * np.matrix(ptx).T).T[":",:: - 1];
        //}

        //public static void path_rotate_y(object path, object angle)
        //{
        //    var ptx = np.append(path, np.ones((np.shape(path)[0], 1)), axis: 1);
        //    return (get_rotate_y_matrix(angle) * np.matrix(ptx).T).T[":",:: - 1];
        //}

        /// <summary>
        /// 已测试
        /// </summary>
        /// <param name="path"></param>
        /// <param name="angle"></param>
        /// <returns></returns>
        public Matrix path_rotate_z(Matrix path, double angle)
        {
            var ptx = path.Append(DenseMatrix.Create(path.RowCount, 1, 1));

            var matrix = get_rotate_z_matrix(angle);
            var tmp = (matrix * ptx.Transpose()).Transpose();

            tmp = tmp.RemoveColumn(tmp.ColumnCount - 1);
            return (Matrix)tmp;
            //var ptxTmp = new double[ptx.GetLength(1), ptx.GetLength(0)];
            //for (int i = 0; i < ptx.GetLength(0); i++)
            //{
            //    for (int j = 0; j < ptx.GetLength(1); j++)
            //    {
            //        ptxTmp[j, i] = ptx[i, j];
            //    }
            //}
            //Console.WriteLine(tmp.ToMatrixString());
            //return tmp.AsArray();
#warning 转置函数
            //return (get_rotate_z_matrix(angle) * np.matrix(ptx).T).T[":",:: - 1];
        }
    }
}
