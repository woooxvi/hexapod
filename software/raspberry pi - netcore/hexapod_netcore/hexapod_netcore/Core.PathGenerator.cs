using hexapod_netcore.Model;
using MathNet.Numerics.LinearAlgebra.Double;
using MathNet.Numerics.RootFinding;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace hexapod_netcore
{
    public partial class Core
    {
        private CAction gen_walk_path(double[,] standby_coordinate, int g_steps = 28, int g_radius = 35, int direction = 0)
        {
            Debug.Assert(g_steps % 4 == 0);

            var halfsteps = Convert.ToInt32(g_steps / 2);
            var semi_circle = semicircle_generator(g_radius, g_steps);
            semi_circle = path_rotate_z(semi_circle, direction);
            var mir_path = semi_circle.Roll(halfsteps);


            var path = new double[g_steps, 6, 3];

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        double value = 0;
                        if (j == 0 || j == 2 || j == 4)
                        {
                            value = semi_circle[i, k];
                        }
                        else if (j == 1 || j == 3 || j == 5)
                        {
                            value = mir_path[i, k];
                        }
                        path[i, j, k] = value;
                    }
                }
            }

            //Console.WriteLine("before path:");
            //Console.WriteLine(printArray(path));

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] += standby_coordinate[j, k];
                    }
                }
            }
            //Console.WriteLine("after path:");
            //Console.WriteLine(printArray(path));
            //Console.WriteLine(mir_path.ToMatrixString());

            return new CMotion(path);
        }

        private CMotion gen_fastwalk_path(double[,] standby_coordinate, int g_steps = 20, double y_radius = 50, double z_radius = 30, double x_radius = 10, bool reverse = false)
        {
            Debug.Assert(g_steps % 2 == 0);
            var halfsteps = Convert.ToInt32(g_steps / 2);

            var path = new double[g_steps, 6, 3];
            var semi_circle_r = semicircle2_generator(g_steps, y_radius, z_radius, x_radius, reverse: reverse);
            var semi_circle_l = semicircle2_generator(g_steps, y_radius, z_radius, -x_radius, reverse: reverse);

            var semi_circle_r_roll = semi_circle_r.Roll(halfsteps);
            var semi_circle_l_roll = semi_circle_l.Roll(halfsteps);

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        if (j == 0 || j == 2)
                        {
                            path[i, j, k] = semi_circle_r[i, k];
                        }
                        else if (j == 1)
                        {
                            path[i, j, k] = semi_circle_r_roll[i, k];
                        }
                        else if (j == 4)
                        {
                            path[i, j, k] = semi_circle_l[i, k];
                        }
                        else if (j == 3 || j == 5)
                        {
                            path[i, j, k] = semi_circle_l_roll[i, k];
                        }
                    }
                }
            }


            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] += standby_coordinate[j, k];
                    }
                }
            }
            return new CMotion(path);
        }

        private CMotion gen_turn_path(double[,] standby_coordinate, int g_steps = 28, double g_radius = 35, string direction = "left")
        {
            Debug.Assert(g_steps % 4 == 0);
            var halfsteps = Convert.ToInt32(g_steps / 2);
            var path = new double[g_steps, 6, 3];
            var semi_circle = semicircle_generator(g_radius, g_steps);
            var mir_path = semi_circle.Roll(halfsteps, axis: 0);
            List<Matrix> matrices = new List<Matrix>();
            if (direction == "left")
            {
                matrices.Add(path_rotate_z(semi_circle, 45));
                matrices.Add(path_rotate_z(mir_path, 0));
                matrices.Add(path_rotate_z(semi_circle, 315));
                matrices.Add(path_rotate_z(mir_path, 225));
                matrices.Add(path_rotate_z(semi_circle, 180));
                matrices.Add(path_rotate_z(mir_path, 135));
            }
            else if (direction == "right")
            {
                matrices.Add(path_rotate_z(semi_circle, 45 + 180));
                matrices.Add(path_rotate_z(mir_path, 0 + 180));
                matrices.Add(path_rotate_z(semi_circle, 315 + 180));
                matrices.Add(path_rotate_z(mir_path, 225 + 180));
                matrices.Add(path_rotate_z(semi_circle, 180 + 180));
                matrices.Add(path_rotate_z(mir_path, 135 + 180));
            }

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] = matrices[j][i, k];
                    }
                }
            }

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] += standby_coordinate[j, k];
                    }
                }
            }

            //return new Dictionary<object, object> {
            //{
            //    "coord",
            //    path + np.tile(standby_coordinate, (g_steps, 1, 1))},
            //{
            //    "type",
            //    "motion"}};
            return new CMotion(path);
        }

        public CMotion gen_climb_path(double[,] standby_coordinate, int g_steps = 28, int y_radius = 20, int z_radius = 80, int x_radius = 30, int z_shift = -30, bool reverse = false)
        {
            Debug.Assert(g_steps % 4 == 0);
            var halfsteps = Convert.ToInt32(g_steps / 2);
            var rpath = semicircle2_generator(g_steps, y_radius, z_radius, x_radius, reverse: reverse);
            rpath.SetSubMatrix(0, 2, rpath.SubMatrix(0, rpath.RowCount, 2, 1) + z_shift);
            var lpath = semicircle2_generator(g_steps, y_radius, z_radius, -x_radius, reverse: reverse);
            lpath.SetSubMatrix(0, 2, lpath.SubMatrix(0, lpath.RowCount, 2, 1) + z_shift);
            var mir_rpath = rpath.Roll(halfsteps, axis: 0);
            var mir_lpath = lpath.Roll(halfsteps, axis: 0);


            var path = new double[g_steps, 6, 3];
            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        if (j == 0 || j == 2)
                        {
                            path[i, j, k] = rpath[i, k];
                        }
                        else if (j == 1)
                        {
                            path[i, j, k] = mir_rpath[i, k];
                        }
                        else if (j == 4)
                        {
                            path[i, j, k] = lpath[i, k];
                        }
                        else if (j == 3 || j == 5)
                        {
                            path[i, j, k] = mir_lpath[i, k];
                        }
                    }
                }
            }

            for (int i = 0; i < path.GetLength(0); i++)
            {
                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] += standby_coordinate[j, k];
                    }
                }
            }

            return new CMotion(path);
        }



        private CMotion gen_rotatex_path(double[,] standby_coordinate, int g_steps = 20, double swing_angle = 15, double y_radius = 15)
        {
            Debug.Assert(g_steps % 4 == 0);
            var quarter = Convert.ToInt32(g_steps / 4);
            var path = new double[g_steps, 6, 3];
            var step_angle = swing_angle / quarter;
            var step_offset = y_radius / quarter;

            var scx = DenseMatrix.OfArray(standby_coordinate).Append(DenseMatrix.Create(6, 1, 1));

            for (int i = 0; i < path.GetLength(0); i++)
            {
                DenseMatrix m;
                switch (i / quarter)
                {
                    case 0:
                        m = get_rotate_x_matrix(swing_angle - i * step_angle);
                        m[1, 3] = -i * step_offset;
                        break;
                    case 1:
                        m = get_rotate_x_matrix(-i * step_angle);
                        m[1, 3] = -y_radius + i * step_offset;
                        break;
                    case 2:
                        m = get_rotate_x_matrix(i * step_angle - swing_angle);
                        m[1, 3] = i * step_offset;
                        break;
                    case 3:
                        m = get_rotate_x_matrix(i * step_angle);
                        m[1, 3] = y_radius - i * step_offset;
                        break;
                    default: throw new Exception("impossibility");
                }

                m = (DenseMatrix)(m * scx.Transpose()).Transpose();
                m = (DenseMatrix)m.RemoveColumn(m.ColumnCount - 1);

                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] = m[j, k];
                    }
                }
            }

            return new CMotion(path);
        }

        private CMotion gen_rotatey_path(double[,] standby_coordinate, int g_steps = 20, double swing_angle = 15, double x_radius = 15)
        {
            Debug.Assert(g_steps % 4 == 0);
            var quarter = Convert.ToInt32(g_steps / 4);
            var path = new double[g_steps, 6, 3];
            var step_angle = swing_angle / quarter;
            var step_offset = x_radius / quarter;

            var scx = DenseMatrix.OfArray(standby_coordinate).Append(DenseMatrix.Create(6, 1, 1));

            for (int i = 0; i < path.GetLength(0); i++)
            {
                DenseMatrix m;
                switch (i / quarter)
                {
                    case 0:
                        m = get_rotate_y_matrix(swing_angle - i * step_angle);
                        m[1, 3] = -i * step_offset;
                        break;
                    case 1:
                        m = get_rotate_y_matrix(-i * step_angle);
                        m[1, 3] = -x_radius + i * step_offset;
                        break;
                    case 2:
                        m = get_rotate_y_matrix(i * step_angle - swing_angle);
                        m[1, 3] = i * step_offset;
                        break;
                    case 3:
                        m = get_rotate_y_matrix(i * step_angle);
                        m[1, 3] = x_radius - i * step_offset;
                        break;
                    default: throw new Exception("impossibility");
                }

                m = (DenseMatrix)(m * scx.Transpose()).Transpose();
                m = (DenseMatrix)m.RemoveColumn(m.ColumnCount - 1);

                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] = m[j, k];
                    }
                }
            }

            return new CMotion(path);
        }

        private CMotion gen_rotatez_path(double[,] standby_coordinate, int g_steps = 20, double z_lift = 4.5, double xy_radius = 1)
        {
            Debug.Assert(g_steps % 4 == 0);
            var path = new double[g_steps, 6, 3];
            var step_angle = 2 * Math.PI / g_steps;
            var scx = DenseMatrix.OfArray(standby_coordinate).Append(DenseMatrix.Create(6, 1, 1));

            for (int i = 0; i < g_steps; i++)
            {
                var x = xy_radius * Math.Cos(i * step_angle);
                var y = xy_radius * Math.Sin(i * step_angle);
                var m = get_rotate_y_matrix(Math.Atan2(x, z_lift) * 180d / Math.PI) * get_rotate_x_matrix(Math.Atan2(y, z_lift) * 180d / Math.PI);

                m = (DenseMatrix)(m * scx.Transpose()).Transpose();
                m = (DenseMatrix)m.RemoveColumn(m.ColumnCount - 1);


                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] = m[j, k];
                    }
                }
            }
            return new CMotion(path);
        }


        public CMotion gen_twist_path(double[,] standby_coordinate, int g_steps = 20, double raise_angle = 3, double twist_x_angle = 20, double twise_y_angle = 12)
        {
            Debug.Assert(g_steps % 4 == 0);
            var quarter = Convert.ToInt32(g_steps / 4);
            var step_x_angle = twist_x_angle / quarter;
            var step_y_angle = twise_y_angle / quarter;
            var scx = DenseMatrix.OfArray(standby_coordinate).Append(DenseMatrix.Create(6, 1, 1));
            var m = get_rotate_x_matrix(raise_angle);
            var path = new double[g_steps, 6, 3];

            for (int i = 0; i < path.GetLength(0); i++)
            {
                DenseMatrix temp;
                switch (i / quarter)
                {
                    case 0:
                        temp = (DenseMatrix?)(m * get_rotate_z_matrix(i * step_x_angle) * get_rotate_x_matrix(i * step_y_angle));
                        break;
                    case 1:
                        temp = (DenseMatrix?)(m * get_rotate_z_matrix((quarter - i) * step_x_angle) * get_rotate_x_matrix((quarter - i) * step_y_angle));
                        break;
                    case 2:
                        temp = (DenseMatrix?)(m * get_rotate_z_matrix(-i * step_x_angle) * get_rotate_x_matrix(i * step_y_angle));
                        break;
                    case 3:
                        temp = (DenseMatrix?)(m * get_rotate_z_matrix((-quarter + i) * step_x_angle) * get_rotate_x_matrix((quarter - i) * step_y_angle));
                        break;
                    default: throw new Exception("impossibility");
                }

                temp = (DenseMatrix)(temp * scx.Transpose()).Transpose();
                temp = (DenseMatrix)temp.RemoveColumn(m.ColumnCount - 1);

                for (int j = 0; j < path.GetLength(1); j++)
                {
                    for (int k = 0; k < path.GetLength(2); k++)
                    {
                        path[i, j, k] = temp[j, k];
                    }
                }
            }
            return new CMotion(path);
        }
    }
}
