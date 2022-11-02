using hexapod_netcore.Model;
using MathNet.Numerics.LinearAlgebra.Double;
using Newtonsoft.Json;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Device.I2c;
using Iot.Device.Pwm;
using Iot.Device.ServoMotor;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Runtime.Intrinsics.X86;
using System.Text;
using System.Threading.Channels;
using System.Threading.Tasks;
using Iot.Device.Mpr121;

namespace hexapod_netcore
{
    public partial class Core
    {
        public ConcurrentQueue<string> cmd_queue;
        private CAction current_motion;
        private bool calibration_mode = false;
        public CConfig config { get; private set; }
        private CLeg[] legs;
        private Dictionary<string, CAction> cmd_dict;
        private CPosture standby_posture;

        private double[] mount_angle;
        private DenseMatrix mount_position;
        private double[] mount_x;
        private double[] mount_y;
        private double root_j1;
        private double j1_j2;
        private double j2_j3;
        private double j3_tip;

        private bool running = false;


        public Core(ConcurrentQueue<string> in_cmd_queue)
        {
            this.cmd_queue = in_cmd_queue;
        }

        public Task Start()
        {
            var configPath = Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory, "config.json");
            var configDefaultPath = Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory, "config.Default.json");

            if (File.Exists(configPath) == false)
            {
                File.Copy(configDefaultPath, configPath);
            }
            var configStr = File.ReadAllText(configPath, Encoding.UTF8);
            if (configStr != null) config = JsonConvert.DeserializeObject<CConfig>(configStr);
            if (config == null) throw new Exception("config error!");


            this.mount_x = this.config.legMountX;
            this.mount_y = this.config.legMountY;
            this.root_j1 = this.config.legRootToJoint1;
            this.j1_j2 = this.config.legJoint1ToJoint2;
            this.j2_j3 = this.config.legJoint2ToJoint3;
            this.j3_tip = this.config.legJoint3ToTip;
            //this.mount_angle = np.array(this.config.legMountAngle) / 180 * Math.PI;
            mount_angle = config.legMountAngle.Select(lma => lma / 180 * Math.PI).ToArray();
            this.mount_position = DenseMatrix.Create(6, 3, 0);
            var mount_position = new double[6, 3];
            this.mount_position.SetSubMatrix(0, 0, DenseMatrix.OfColumnArrays(this.mount_x));
            this.mount_position.SetSubMatrix(0, 1, DenseMatrix.OfColumnArrays(this.mount_y));
            //for (int i = 0; i < mount_position.GetLength(0); i++)
            //{
            //    mount_position[i, 0] = config.legMountX[i];
            //    mount_position[i, 1] = config.legMountY[i];
            //}


            //this.pca_right = ServoKit(channels = 16, address = 0x40, frequency = 120);
            //this.pca_left = ServoKit(channels = 16, address = 0x41, frequency = 120);
            var pca_left = new ServoKit(channels: 16, address: 1);
            var pca_right = new ServoKit(channels: 16, address: 2);

            legs = new CLeg[6]
            {
                new CLeg(0, pca_left.Take( 6,   7,  8 ), correction: this.config.leg0Offset),
                new CLeg(1, pca_left.Take( 3,   4,  5 ), correction: this.config.leg1Offset),
                new CLeg(2, pca_left.Take( 0,   1,  2 ), correction: this.config.leg2Offset),
                new CLeg(3, pca_right.Take(15,  14, 13), correction: this.config.leg3Offset),
                new CLeg(4, pca_right.Take(7,   11, 6 ), correction: this.config.leg4Offset),
                new CLeg(5, pca_right.Take(0,   2,  5 ), correction : this.config.leg5Offset),
            };

            this.standby_posture = this.gen_posture(60, 75);
            this.current_motion = this.standby_posture;

            this.cmd_dict = new Dictionary<string, CAction>();
            cmd_dict.Add(CMD_STANDBY, standby_posture);
            cmd_dict.Add(CMD_LAYDOWN, gen_posture(0, 15));
            cmd_dict.Add(CMD_WALK_0, gen_walk_path(this.standby_posture.coord, direction: 0));
            cmd_dict.Add(CMD_WALK_180, gen_walk_path(this.standby_posture.coord, direction: 180));
            cmd_dict.Add(CMD_WALK_R45, gen_walk_path(this.standby_posture.coord, direction: 315));
            cmd_dict.Add(CMD_WALK_R90, gen_walk_path(this.standby_posture.coord, direction: 270));
            cmd_dict.Add(CMD_WALK_R135, gen_walk_path(this.standby_posture.coord, direction: 225));
            cmd_dict.Add(CMD_WALK_L45, gen_walk_path(this.standby_posture.coord, direction: 45));
            cmd_dict.Add(CMD_WALK_L90, gen_walk_path(this.standby_posture.coord, direction: 90));
            cmd_dict.Add(CMD_WALK_L135, gen_walk_path(this.standby_posture.coord, direction: 135));
            cmd_dict.Add(CMD_FASTFORWARD, gen_fastwalk_path(this.standby_posture.coord));
            cmd_dict.Add(CMD_FASTBACKWARD, gen_fastwalk_path(this.standby_posture.coord, reverse: true));
            cmd_dict.Add(CMD_TURNLEFT, gen_turn_path(this.standby_posture.coord, direction: "left"));
            cmd_dict.Add(CMD_TURNRIGHT, gen_turn_path(this.standby_posture.coord, direction: "right"));
            cmd_dict.Add(CMD_CLIMBFORWARD, gen_climb_path(this.standby_posture.coord, reverse: false));
            cmd_dict.Add(CMD_CLIMBBACKWARD, gen_climb_path(this.standby_posture.coord, reverse: true));
            cmd_dict.Add(CMD_ROTATEX, gen_rotatex_path(this.standby_posture.coord));
            cmd_dict.Add(CMD_ROTATEY, gen_rotatey_path(this.standby_posture.coord));
            cmd_dict.Add(CMD_ROTATEZ, gen_rotatez_path(this.standby_posture.coord));
            cmd_dict.Add(CMD_TWIST, gen_twist_path(this.standby_posture.coord));

            this.running = true;
            return Task.Run(core);
        }

        public void Stop()
        {
            this.running = false;
        }

        private CPosture gen_posture(double j2_angle, double j3_angle)
        {
            var j2_rad = j2_angle / 180d * Math.PI;
            var j3_rad = j3_angle / 180d * Math.PI;
            var posture = new double[6, 3];
            for (int i = 0; i < posture.GetLength(0); i++)
            {

                posture[i, 0] = (double)(mount_x[i] + (root_j1 + j1_j2 + (j2_j3 * Math.Sin(j2_rad)) + j3_tip * Math.Cos(j3_rad)) * Math.Cos(mount_angle[i]));
                posture[i, 1] = (double)(config.legMountY[i] + (root_j1 + j1_j2 + (j2_j3 * Math.Sin(j2_rad)) + j3_tip * Math.Cos(j3_rad)) * Math.Sin(mount_angle[i]));
                posture[i, 2] = (double)(j2_j3 * Math.Cos(j2_rad) - j3_tip * Math.Sin(j3_rad));
            }
            return new CPosture()
            {
                coord = posture
            };
        }

        private void core()
        {
            while (running)
            {
                string cmd_string = null;
                if (cmd_queue.TryDequeue(out cmd_string))
                {
                    cmd_handler(cmd_string);
                }

                if (!this.calibration_mode)
                {
                    if (this.current_motion is CMotion cMotion)
                        this.motion(cMotion.coord);
                    else if (this.current_motion is CPosture cPosture)
                        this.posture(cPosture.coord);
                }
            }
        }

        public void posture(double[,] coordinate)
        {
            var angles = this.inverse_kinematics(coordinate);

            this.legs[0].move_junctions(angles.GetPart(0) as double[]);
            this.legs[5].move_junctions(angles.GetPart(5) as double[]);

            this.legs[1].move_junctions(angles.GetPart(1) as double[]);
            this.legs[4].move_junctions(angles.GetPart(4) as double[]);

            this.legs[2].move_junctions(angles.GetPart(2) as double[]);
            this.legs[3].move_junctions(angles.GetPart(3) as double[]);
        }

        public void motion(double[,,] path)
        {
            for (int p_idx = 0; p_idx < path.GetLength(0); p_idx++)
            {
                double[,] dest = path.GetPart(p_idx) as double[,];
                double[,] angles = inverse_kinematics(dest);
                this.legs[0].move_junctions(angles.GetPart(0) as double[]);
                this.legs[5].move_junctions(angles.GetPart(5) as double[]);

                this.legs[1].move_junctions(angles.GetPart(1) as double[]);
                this.legs[4].move_junctions(angles.GetPart(4) as double[]);

                this.legs[2].move_junctions(angles.GetPart(2) as double[]);
                this.legs[3].move_junctions(angles.GetPart(3) as double[]);

                string cmd_string = null;
                if (this.cmd_queue.TryDequeue(out cmd_string))
                {
                    Console.WriteLine("interrput");
                    this.cmd_handler(cmd_string);
                }
            }
        }

        public double[,] inverse_kinematics(double[,] dest)
        {
            var temp_dest = DenseMatrix.OfArray(dest) - this.mount_position;
            var local_dest = DenseMatrix.Create(dest.GetLength(0), dest.GetLength(1), 0);
            for (int i = 0; i < local_dest.RowCount; i++)
            {
                local_dest[i, 0] = temp_dest[i, 0] * Math.Cos(mount_angle[i]) + temp_dest[i, 1] * Math.Sin(mount_angle[i]);
                local_dest[i, 1] = temp_dest[i, 0] * Math.Sin(mount_angle[i]) + temp_dest[i, 1] * Math.Cos(mount_angle[i]);
                local_dest[i, 2] = temp_dest[i, 2];
            }

            var angles = new double[6, 3];
            for (int i = 0; i < angles.GetLength(0); i++)
            {
                for (int j = 0; j < angles.GetLength(1); j++)
                {
                    if (j == 0)
                    {
                        var x = local_dest[i, 0] - root_j1;
                        var y = local_dest[i, 1];
                        angles[i, j] = -(Math.Atan2(y, x) * 180 / Math.PI) + 90;
                    }
                    else
                    {
                        var x = local_dest[i, 0] - root_j1;
                        var y = local_dest[i, 1];
                        x = Math.Sqrt(x * x + y * y) - j1_j2;
                        y = local_dest[i, 2];
                        var ar = Math.Atan2(y, x);
                        var lr2 = x * x + y * y;
                        var lr = Math.Sqrt(lr2);
                        var a1 = Math.Acos((lr2 + this.j2_j3 * this.j2_j3 - this.j3_tip * this.j3_tip) / (2 * this.j2_j3 * lr));
                        var a2 = Math.Acos((lr2 - this.j2_j3 * this.j2_j3 + this.j3_tip * this.j3_tip) / (2 * this.j3_tip * lr));
                        if (j == 1)
                        {
                            angles[i, j] = 90 - ((ar + a1) * 180 / Math.PI);
                        }
                        else
                        {
                            //j==2
                            angles[i, j] = (90 - ((a1 + a2) * 180 / Math.PI)) + 90;
                        }
                    }

                }
            }

            return angles;
        }

        private void cmd_handler(string cmd_string)
        {
            var data = cmd_string.Split(':').Reverse().ToArray()[1];
            if (data == CMD_CALIBRATION)
            {
                this.calibration_mode = true;
                for (int i = 0; i < 6; i++)
                {
                    this.legs[i].reset(true);
                }
            }
            else if (data == CMD_NORMAL)
            {
                this.calibration_mode = false;
            }
            else
            {
                if (this.calibration_mode)
                {
                    this.calibration_cmd_handler(data);
                }
                else
                {
                    this.current_motion = this.cmd_dict.GetValueOrDefault(data, this.standby_posture);
                }
            }
        }

        private void calibration_cmd_handler(string data)
        {
            var data_array = data.Split(',');
            if (data_array.Length == 4)
            {
                var op = data_array[0].Trim();

                var leg_idx = Convert.ToInt32(data_array[1]);
                if (leg_idx < 0 || leg_idx > 5) return;

                var joint_idx = Convert.ToInt32(data_array[2]);
                if (joint_idx < 0 || joint_idx > 2) return;

                var angle = Convert.ToSingle(data_array[3]);
                if (op == "angle")
                {
                    this.legs[leg_idx].set_angle(joint_idx, angle);
                }
                else if (op == "offset")
                {
                    this.legs[leg_idx].correction[joint_idx] = angle;
                    this.legs[leg_idx].reset(true);

                    var config_str = $"leg{leg_idx}Offset";

                    this.config.SetOffset(leg_idx, this.legs[leg_idx].correction);

                    File.WriteAllText(Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory, "config.json"), JsonConvert.SerializeObject(config, Newtonsoft.Json.Formatting.Indented), Encoding.UTF8);

                }
            }
        }


        const string CMD_STANDBY = "standby";
        const string CMD_LAYDOWN = "laydown";

        const string CMD_WALK_0 = "walk0";
        const string CMD_WALK_180 = "walk180";


        const string CMD_WALK_R45 = "walkr45";
        const string CMD_WALK_R90 = "walkr90";
        const string CMD_WALK_R135 = "walkr135";


        const string CMD_WALK_L45 = "walkl45";
        const string CMD_WALK_L90 = "walkl90";
        const string CMD_WALK_L135 = "walkl135";

        const string CMD_FASTFORWARD = "fastforward";
        const string CMD_FASTBACKWARD = "fastbackward";

        const string CMD_TURNLEFT = "turnleft";
        const string CMD_TURNRIGHT = "turnright";

        const string CMD_CLIMBFORWARD = "climbforward";
        const string CMD_CLIMBBACKWARD = "climbbackward";

        const string CMD_ROTATEX = "rotatex";
        const string CMD_ROTATEY = "rotatey";
        const string CMD_ROTATEZ = "rotatez";

        const string CMD_TWIST = "twist";

        const string CMD_CALIBRATION = "calibration";
        const string CMD_NORMAL = "normal";


        public void UnitTest()
        {
            gen_walk_path(null);
        }

        private string printArray(double[,] a)
        {
            string res = "[";
            for (int i = 0; i < a.GetLength(0); i++)
            {
                res += "[";
                for (int j = 0; j < a.GetLength(1); j++)
                {
                    if (j % 4 == 0)
                    {
                        if (j == 0)
                            res += "\t";
                        else
                            res += (System.Environment.NewLine + "\t");
                    }
                    res += a[i, j].ToString("e");
                    res += "\t";
                }
                res += "]";
                if (i == a.GetLength(0) - 1)
                {
                    res += "]";
                }
                res += System.Environment.NewLine;
            }
            Console.WriteLine(res);
            return res;
        }

        private string printArray(double[,,] a)
        {
            string res = "[";
            for (int i = 0; i < a.GetLength(0); i++)
            {
                res += "[";
                for (int j = 0; j < a.GetLength(1); j++)
                {
                    res += "[";
                    for (int k = 0; k < a.GetLength(2); k++)
                    {

                        if (k % 4 == 0)
                        {
                            if (k == 0)
                                res += "\t";
                            else
                                res += (System.Environment.NewLine + "\t");
                        }
                        res += a[i, j, k].ToString("e");
                        res += "\t";
                    }
                    res += "]";
                    if (j == a.GetLength(0) - 1)
                    {
                        res += "]";
                    }
                    res += System.Environment.NewLine;
                }
                res += "]";
                if (i == a.GetLength(0) - 1)
                {
                    res += "]";
                }
                res += System.Environment.NewLine;
            }
            Console.WriteLine(res);
            return res;
        }
    }
}
