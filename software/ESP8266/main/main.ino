#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <ESP8266WebServer.h>
#include <Adafruit_PWMServoDriver.h>
#include <LinkedList.h>
#include <Ticker.h>


const String ssid = "www.xiaoqiumi.com";
const String passwd = "18648801440";

// const String ssid = "Leray24";
// const String passwd = "leray0410";

const uint8_t MAX_STEP = 10;
uint8_t FRAME_RATE = 15;
const uint8_t LEG_COUNT = 6;
const uint8_t JOINT_COUNT = 3;

Ticker myTicker;

int tickerTotal = 0;

String httpCommand = "";
String postureCommand = "";


ESP8266WebServer server;

Adafruit_PWMServoDriver pwm_l = Adafruit_PWMServoDriver(0x40);
Adafruit_PWMServoDriver pwm_r = Adafruit_PWMServoDriver(0x41);
#define MIN_PULSE_WIDTH 500
#define MAX_PULSE_WIDTH 2500
#define FREQUENCY 50

struct Leg {
  // uint8_t board;
  Adafruit_PWMServoDriver* pwm;
  uint8_t port;
  // float angle;
  float offset;
  // bool reverse;
};

const Leg legs[LEG_COUNT][JOINT_COUNT] = {
  {
    //右前  0
    { &pwm_r, 15, 0.0 },
    { &pwm_r, 14, 0.0 },
    { &pwm_r, 13, 0.0 },
  },
  {
    //右中  1
    { &pwm_r, 12, 0.0 },
    { &pwm_r, 11, 0.0 },
    { &pwm_r, 10, 0.0 },
  },
  {
    //右后  2
    { &pwm_r, 9, 0.0 },
    { &pwm_r, 8, 0.0 },
    { &pwm_r, 7, 0.0 },
  },
  {
    //左后  3
    { &pwm_l, 6, 0.0 },   //坏了？
    { &pwm_l, 7, 0.0 },
    { &pwm_l, 8, 0.0 },   //坏了？
  },
  {
    //左中  4
    { &pwm_l, 3, 0.0 },
    { &pwm_l, 4, 0.0 },
    { &pwm_l, 5, 0.0 },
  },
  {
    //左前  5
    { &pwm_l, 0, 0.0 },
    { &pwm_l, 1, 0.0 },
    { &pwm_l, 2, 0.0 },
  },
}; 

float legStatus[LEG_COUNT][JOINT_COUNT] = {
  {90, 90, 90},
  {90, 90, 90},
  {90, 90, 90},
  {90, 90, 90},
  {90, 90, 90},
  {90, 90, 90},
};

struct Step {
  uint8_t posture[LEG_COUNT][JOINT_COUNT];
  uint16_t elapsed;
};

const Step CMD_forward[MAX_STEP] = {
  { {{131, 137, 54}, {90, 133, 63}, {94, 48, 118}, {90, 144, 63}, {97, 134, 44}, {90, 124, 45}}, 1500 },
  { {{121, 127, 64}, {80, 123, 73}, {84, 58, 118}, {100, 134, 73}, {87, 124, 54}, {80, 114, 55}}, 1500 },
  { {{111, 117, 74}, {70, 113, 83}, {74, 68, 118}, {110, 124, 83}, {77, 114, 64}, {70, 104, 65}}, 1500 },
  { {{121, 127, 64}, {80, 123, 73}, {84, 58, 118}, {100, 134, 73}, {87, 124, 54}, {80, 114, 55}}, 1500 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 0 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
};

const Step CMD_back[MAX_STEP] = {
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 0 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
};

const Step CMD_left[MAX_STEP] = {
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 0 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
};

const Step CMD_right[MAX_STEP] = {
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 1000 },
  { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 0 },
};

Step currStep = { { {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90}, {90, 90, 90} }, 0 };

//                      首步首循  首步骤首循后  首步n循后 首步N0循后 二步首循前   二步首循后  二步n循后 二步N1循后  执行完M步后首次循环前
//------------------------------------------------------------------------------------------------------------------------------------
// currStepIdx        | 0         0             0         0      →  1             1         1         1           0
// currStepFrameIdx   | 0         1             n         N0     →  0             1         n         N1          0
// currStepFrameCount | 0    →    N0            N0        N0     →  0     →       N1        N1        N1          N0
// cmdRound           | 0         0             0         0      →  1             1         1         1           M

const Step* currTask;
// Step const (*currTask)[MAX_STEP] = NULL;
uint8_t currTaskStepCount = 0;

uint8_t currStepIdx = 0;
uint8_t currStepFrameIdx = 0;
uint8_t currStepFrameCount = 0;
int cmdRound = 0;
uint16_t elapsedPreadd = 2000;

//减速
float taskSacle = 1.0;
uint8_t printTaskLevel = 0;

void setup() {
  Serial.println("Enter setup");
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(0, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  // setupPWM();
  pwm_l.begin();
  pwm_r.begin();
  pwm_l.setPWMFreq(FREQUENCY);  // Analog servos run at ~50 Hz updates
  pwm_r.setPWMFreq(FREQUENCY);  // Analog servos run at ~50 Hz updates

  // setupWifi();
  // 设置WiFi运行模式为无线终端模式
  WiFi.mode(WIFI_STA);
  // // 为当前设备配置固定IP
  // if (!WiFi.config(host, gateway, netmask)) {
  //   Serial.println("Can't config wifi.");
  // }
  Serial.println("Connecting to " + ssid);
  // 连接WiFi
  WiFi.begin(ssid, passwd);
  // 判断是否连接成功
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(100);
  }
  Serial.println("");
  Serial.println("Connected to " + ssid);

  // setupWS();
  server.onNotFound(httpCommandHandler);
  server.begin(80);
  Serial.println("HTTP server started");

  myTicker.attach_ms(1000 / FRAME_RATE, moveFrame);

  delay(1000);
  
  Serial.print("Current ip address is ");
  Serial.println(WiFi.localIP());

}


void moveFrame(){
  tickerTotal++;
  if(currTask != NULL || currStep.elapsed != 0){
    if(currTask != NULL){
      currStep.elapsed = currTask[currStepIdx].elapsed;
      for(int legIdx = 0; legIdx < LEG_COUNT; legIdx++) {
        for(int jointIdx = 0; jointIdx < JOINT_COUNT; jointIdx++) {
          currStep.posture[legIdx][jointIdx] = currTask[currStepIdx].posture[legIdx][jointIdx];
        }
      }
    }
    if(currStepFrameIdx==0){
      Serial.print("=================进入步骤, cmdRound=");
      Serial.print(cmdRound);
      Serial.print(", currStepIdx=");
      Serial.print(currStepIdx);
      // Serial.print(", currStepFrameIdx=");
      // Serial.print(currStepFrameIdx);

      Serial.print(" elapsed=(");
      Serial.print(currStep.elapsed);

      uint16_t elapsed = currStep.elapsed;
        //首次进入加多三秒
      if(cmdRound==0) { 
        Serial.print("+");
        Serial.print(elapsedPreadd);
        elapsed += elapsedPreadd;
      }
      elapsed *= taskSacle;
      Serial.print(")*");
      Serial.print(taskSacle);
      Serial.print(" = ");
      Serial.print(elapsed);

      //计算需要的步骤数 currStepFrameCount == 0
      currStepFrameCount = ceil(elapsed / 1000.0 * FRAME_RATE);
      Serial.print(", currStepFrameCount=");
      Serial.print(currStepFrameCount);

    }
    // float legStatusPrev[LEG_COUNT][JOINT_COUNT];   ); Serial.print(
    uint8_t currStepFrameLess = currStepFrameCount-currStepFrameIdx;
    if(printTaskLevel==0) {
      Serial.println("");
      Serial.print("执行Step:"); Serial.print(currStepIdx); Serial.print(", Frame:"); Serial.print(currStepFrameIdx); Serial.print("/"); Serial.print(currStepFrameCount); Serial.print(", cmdRound:"); Serial.print(cmdRound);
    }

    for(int legIdx = 0; legIdx < LEG_COUNT; legIdx++) {
      if(printTaskLevel==0 || currStepFrameIdx==0) Serial.print("\n");
      for(int jointIdx = 0; jointIdx < JOINT_COUNT; jointIdx++) {
        float angleLess = currStep.posture[legIdx][jointIdx] - legStatus[legIdx][jointIdx];
        float angleLessStep = angleLess / currStepFrameLess;
        float targetAngle = legStatus[legIdx][jointIdx] + angleLessStep;
        // legStatusPrev[legIdx][jointIdx] = legStatus[legIdx][jointIdx];
        float prevAngle = exeServoMotor(legIdx, jointIdx, targetAngle, true, true, false);
        if(printTaskLevel==0){
          if(prevAngle >= 0){
            Serial.print(formatFloat(prevAngle)); Serial.print(" + "); Serial.print(formatFloat(angleLessStep)); Serial.print(" → "); Serial.print(formatFloat(targetAngle)); Serial.print(", ");
          }else{
            Serial.print(formatFloat(legStatus[legIdx][jointIdx])); Serial.print(" + "); Serial.print(formatFloat(angleLessStep)); Serial.print(" → error, ");
          }
        }else if(currStepFrameIdx==0){
          Serial.print(formatFloat(prevAngle)); Serial.print(" + "); Serial.print(formatFloat(angleLess)); Serial.print(" → "); Serial.print(formatFloat(currStep.posture[legIdx][jointIdx])); Serial.print(", ");
        }
      }
      // legIdx++;
    }
    currStepFrameIdx++;
    if(printTaskLevel==0 || currStepFrameIdx==currStepFrameCount) Serial.println("");
    else Serial.print(".");
    if(currStepFrameIdx==currStepFrameCount){
      if(currTask == NULL){
        stopTask();
      }else{
        //x步Nx循后
        currStepIdx++;
        currStepFrameIdx=0;
        currStepFrameCount=0;
        cmdRound++;
        if(currStepIdx==currTaskStepCount){
          //下一次循环
          currStepIdx=0;
        }
      }
    }
  }

  
      // uint8_t maxDistance = 0;
      // for(uint8_t stepIdx = 0; stepIdx < sizeof(currTask); stepIdx++){
        

      //   if(stepIdx+1<sizeof(currTask) && currTask[stepIdx].interval == 0) break;
      // }
}


void loop() {
  // int start = tickerTotal;
  String command = Serial.readString();
  if (command != "") {
    Serial.println("");
    Serial.println("got Serial command:" + command);
  }
    // Serial.print("cost time(Serial):");
    // Serial.println((tickerTotal - start) / 10.0);
    // start=tickerTotal;


  if (command == "") {
    server.handleClient();
    command = httpCommand;
    httpCommand = "";
    // Serial.print("cost time(Http):");
    // Serial.println((tickerTotal - start) / 10.0);
    // start=tickerTotal;
    if(command != ""){
      Serial.println("");
      Serial.println("got Http command:" + command);
    }
  }

  if (command == "") {
    command = postureCommand;
    if(command != ""){
      Serial.println("");
      Serial.println("got Posture command:" + command);
    }
  }

  if (command != "") {
    String portStr = command.substring(1, 3);
    String boardStr = command.substring(0, 1);
    String angleStr = command.substring(3);
    Adafruit_PWMServoDriver* pwm;
    if (boardStr == "l") {
      pwm = &pwm_l;
    } else if (boardStr == "r") {
      pwm = &pwm_r;
    } else {
      Serial.print("?");
    }
    int port = portStr.toInt();
    int angle = angleStr.toInt();
    Serial.print("set ");
    Serial.print(boardStr);
    Serial.print(port);
    Serial.print(" to ");
    Serial.println(angle);
    pwm->setPWM(port, 0, pulseWidth(angle));
  }else{
  }
}

void httpCommandHandler() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  String command = server.uri().substring(1);
  String data;
  int len = server.arg(0).length();
  if (len > 0) data = server.arg(0);


  if (command == "yo"){
    server.send(200, "text/plain", "yo");
    Serial.println("新的问候");


  } else if (command == "stop"){
    stopTask();
    server.send(200, "text/plain", command);


  } else if (command =="cmd" || command == "move") {
    bool withFix = (command == "move");
    stopTask();
    JsonDocument doc;
    deserializeJson(doc, data);
    uint8_t legIdx = doc["LegIdx"].as<uint8_t>();
    uint8_t jointIdx = doc["JointIdx"].as<uint8_t>();
    float angle = doc["Angle"].as<float>();
    bool hasErr = false;
    if (legIdx < 0 || legIdx >= LEG_COUNT) {
      Serial.print("illegal legIdx");
      Serial.println(legIdx);
      hasErr = true;
    }
    if (jointIdx < 0 || jointIdx >= JOINT_COUNT) {
      Serial.print("illegal jointIdx");
      Serial.println(jointIdx);
      hasErr = true;
    }
    if(hasErr == false){
      exeServoMotor(legIdx, jointIdx, angle, withFix, true, true);
    }
    server.send(200, "text/plain", data);


  } else if (command =="cmdpos" || command == "movepos") {
    bool withFix = (command == "movepos");
    stopTask();
    // Serial.println(command + ",withFix" + withFix);
    JsonDocument doc;
    deserializeJson(doc, data);
    JsonArray legAngles = doc.as<JsonArray>();

    uint8_t legIdx = 0, jointIdx = 0;
    for(JsonArray legAngle : legAngles){
      jointIdx=0;
      for(JsonVariant jointAngle : legAngle){
        float angle = jointAngle.as<uint8_t>();
        // Serial.print("l:"); Serial.print(legIdx); Serial.print("j:"); Serial.print(jointIdx); Serial.print("angle:"); Serial.println(angle);
        currStep.posture[legIdx][jointIdx] = angle;
        // exeServoMotor(legIdx, jointIdx, angle, withFix, true, true);
        jointIdx++;
      }
      legIdx++;
    }
    currStep.elapsed = 1000;
    startTask(NULL, 0);

    // // Serial.println("read data done:" + data);
    // uint8_t legIdx = 0, jointIdx = 0;
    // for(JsonArray legAngle : legAngles){
    //   jointIdx=0;
    //   for(JsonVariant jointAngle : legAngle){
    //     float angle = jointAngle.as<uint8_t>();
    //     exeServoMotor(legIdx, jointIdx, angle, withFix, true, true);
    //     jointIdx++;
    //   }
    //   legIdx++;
    // }
    Serial.print("legIdx:"); Serial.print(legIdx); Serial.print(", jointIdx:"); Serial.println(jointIdx);
    server.send(200, "text/plain", data);

 
  } else if (command =="setting") {
    JsonDocument doc;
    deserializeJson(doc, data);
    if(doc.containsKey("TaskSacle")) taskSacle = doc["TaskSacle"].as<float>();
    if(doc.containsKey("PrintTaskLevel")) printTaskLevel = doc["PrintTaskLevel"].as<uint8_t>();
    if(doc.containsKey("FrameRate")) FRAME_RATE = doc["FrameRate"].as<uint8_t>();
    server.send(200, "text/plain", data);

  } else if (command.startsWith("task/")) {
    command = command.substring(5);
    const Step* _currTask = NULL;
    if( command == "forward" ){
      _currTask = CMD_forward;
    }else if ( command == "back" ){
      _currTask = CMD_back;
    }else if ( command == "left" ){
      _currTask = CMD_left;
    }else if ( command == "right" ){
      _currTask = CMD_right;
    }
    if(_currTask == NULL){
      server.send(200, "text/plain", "unknow task:" + command);
      Serial.println("unknow task:" + command);
      return;
    }else{ 
      stopTask();
      startTask(_currTask, 2000);
      Serial.println("");
      server.send(200, "text/plain", "into task:" + command + ",stepCount:" + currTaskStepCount);
      Serial.println("into task:" + command);
    }

  }
}

void startTask(const Step* _currTask, uint16_t _elapsedPreadd){
  // 移动？
  // currTask[0].elapsed = 0;
  // for(uint8_t i = 0; i < MAX_STEP; i++){
  //   if(i==0) currTask[i].elapsed = _currTask[i].elapsed;
  //   for(uint8_t legIdx = 0; legIdx < MAX_STEP; legIdx++){
  //     for(uint8_t jointIdx = 0; jointIdx < MAX_STEP; jointIdx++){
  //       currTask[i].posture[legIdx][jointIdx] = _currTask[i].posture[legIdx][jointIdx];
  //     }
  //   }
  // }
  if(_currTask == NULL){
    currTaskStepCount = 1;
  } else {
    for(uint8_t i = 0; i < MAX_STEP; i++){
      if(_currTask[i].elapsed == 0) {
        currTaskStepCount = i;
        break;
      }
    }
  }

  currStepIdx = 0;
  currStepFrameIdx = 0;
  currStepFrameCount = 0;
  cmdRound = 0;
  elapsedPreadd = _elapsedPreadd;
  currTask = _currTask;
  // currTask[i].elapsed = _currTask[i].elapsed;
}

void stopTask(){
  currTask = NULL;
  currStep.elapsed = 0;
  currStepIdx = 0;
  currStepFrameIdx = 0;
  currStepFrameCount = 0;
  cmdRound = 0;
  currTaskStepCount = 0;
  Serial.println("Task Stoped!");
}

//成功返回旧角度，否则返回-1
float exeServoMotor(uint8_t legIdx, uint8_t jointIdx, float angle, bool withFix, bool force, bool log) {
  const Leg* _leg = &legs[legIdx][jointIdx];
  if(log){
    Serial.print("legIdx = ");Serial.print(legIdx);Serial.print(";");
    Serial.print("jointIdx = ");Serial.print(jointIdx);Serial.print(";");
  }
  float angleTruth = angle;
  if ( withFix ) {
    angleTruth = angle + _leg -> offset;
  }
  if (angleTruth < 0 || angleTruth > 180) {
    if(log){
      Serial.print("illegal angle:");
      Serial.print(angleTruth);
      if(angle != angleTruth) Serial.print("["); Serial.print(angle); Serial.print("]");
      Serial.println("");
    }
    return -1;  //illegal angle
  } else if (!force && legStatus[legIdx][jointIdx] == angleTruth) {
    if(log){
      Serial.print("unchange angle:");
      Serial.print(angleTruth);
      if(angle != angleTruth) {Serial.print("["); Serial.print(angle); Serial.print("]");}
      Serial.println("");
    }
    return -2;  //unchange angle
  } else {
    float prevAngle = legStatus[legIdx][jointIdx];
    if(log){
      // 通过串口监视器输出解析后的数据信息
      Serial.print("angleNow = ");Serial.print(prevAngle);Serial.print(";");
      Serial.print(" -> "); Serial.print(angleTruth);
      Serial.println();
    }
    _leg->pwm->setPWM(_leg->port, 0, pulseWidth(angleTruth)); 
    legStatus[legIdx][jointIdx] = angleTruth;
    return prevAngle;
    // pwm.setPWM(1, 0, pulseWidth(180));   // 1号接口输出180度
  }
}

// PWM舵机控制函数
float pulseWidth(float angle) {
  float pulse_wide, analog_value;
  pulse_wide = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);
  analog_value = float(pulse_wide) / 1000000.0 * FREQUENCY * 4096.0;
  return analog_value;
}

String formatFloat(float value){  
    // 确保值不超过128  
    if (value > 128.0) {  
        value = 128.0;  
    }  
  
    // 分离整数部分和小数部分  
    int intPart = static_cast<int>(value);  
    float fracPart = value - intPart;  
  
    // 格式化整数部分，确保有三位数字（前面补0）  
    char intStr[4];  
    snprintf(intStr, sizeof(intStr), "%03d", intPart);  
  
    // 格式化小数部分，保留一位小数（后面补0）  
    char fracStr[3];  
    if (fracPart < 0.1) {  
        strcpy(fracStr, "00"); // 如果小数部分为0，则直接赋值为"00"  
    } else {  
        int roundedFrac = static_cast<int>(round(fracPart * 10)); // 四舍五入到最接近的整数  
        snprintf(fracStr, sizeof(fracStr), "%01d0", roundedFrac); // 转换为字符串，并确保有两位数字（第二位为0）  
    }  
  
    // 合并整数部分和小数部分  
    String result = String(intStr) + "." + String(fracStr[0]); // 注意：这里只取了fracStr的第一位，因为我们已经确保了它只有一位有效数字  
    return result;  
}