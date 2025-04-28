#include "secrets.h"
#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include "WiFi.h"
#include <PubSubClient.h>
#include "esp_camera.h"
#include <ArduinoJson.h>
#include "Base64.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
#define LED               33
#define FLASH             4
#define BUZZER            14

const int TRIG = 2;
const int ECHO = 13;
const int ALARM = 12;
int uzaklik = 0;
int sure;
bool shouldGrabImage = false;

#define ESP32CAM_PUBLISH_TOPIC   "esp32/pub"
#define ESP32CAM_SUBSCRIBE_TOPIC "esp32/sub"
#define ESP32CAM_CONT_CONNECTION "esp32/cont"


const int bufferSize = 1024 * 23; // 23552 bytes
WiFiClientSecure net = WiFiClientSecure();
//MQTTClient client = MQTTClient(bufferSize);
MQTTClient client = MQTTClient(bufferSize);

void callback(String &topic, String &payload) {

  if(topic == ESP32CAM_SUBSCRIBE_TOPIC && payload == "1"){
    digitalWrite(ALARM,HIGH);
    delay(3000);
    digitalWrite(ALARM,LOW);
  }

}

void connectAWS()
{

  Serial.println("\n\n=====================");
  Serial.println("Connecting to Wi-Fi");
  Serial.println("=====================\n\n");

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  // Configure WiFiClientSecure to use the AWS IoT device credentials
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  // Connect to the MQTT broker on the AWS endpoint we defined earlier

  //client.setKeepAlive(120000);
  //client.setCleanSession(true);

  Serial.println("\n\n=====================");
  Serial.println("Connecting to AWS IOT");
  Serial.println("=====================\n\n");

  while (!client.connect(THINGNAME)) {
    Serial.print(".");
    delay(100);
  }

  if(!client.connected()){
    Serial.println("AWS IoT Timeout!");
    ESP.restart();
    return;
  }else {
    int result =  client.subscribe(ESP32CAM_SUBSCRIBE_TOPIC);
    Serial.print("subscribed : ");
    Serial.println(result);
  }

  Serial.println("\n\n=====================");
  Serial.println("AWS IoT Connected!");
  Serial.println("=====================\n\n");
}

void sensorInit(){
  sensor_t * s = esp_camera_sensor_get();
  s->set_vflip(s,1);
}


void cameraInit(){
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QQVGA; // 640x480
  config.jpeg_quality = 22;
  config.fb_count = 1;
  config.grab_mode = CAMERA_GRAB_LATEST;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
    return;
  }
  Serial.printf("init okay");
  sensorInit();
}

void grabImage(){
  esp_camera_fb_return(esp_camera_fb_get());
  camera_fb_t * fb = esp_camera_fb_get();
  if(fb != NULL && fb->format == PIXFORMAT_JPEG && fb->len < bufferSize){

  JsonDocument jsonDoc;
  const int size = base64_enc_len(fb->len);
  char serialDoc[3000];
  char *input = (char *)fb->buf;
  char output[base64_enc_len(fb->len)];
  memset(output, 0, sizeof(output)); // Output dizisini sıfırla
  base64_encode(output, input, fb->len);
  jsonDoc["image"] = output;
  serializeJson(jsonDoc,serialDoc);
  Serial.println(output);
  Serial.println(base64_enc_len(fb->len));
  Serial.println(serialDoc);
  

    Serial.print("Image Length: ");
    Serial.print(fb->len);
    Serial.print("\t Publish Image: ");
    bool result = client.publish(ESP32CAM_PUBLISH_TOPIC,serialDoc);
    Serial.println(result);

    if(!result){
      ESP.restart();
    }
  }else{
    
  }
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  client.begin(AWS_IOT_ENDPOINT, 8883, net);
  client.onMessage(callback);

  pinMode(LED,OUTPUT);
  pinMode(BUZZER,OUTPUT);
  pinMode(TRIG,OUTPUT);
  pinMode(ALARM,OUTPUT);
  pinMode(ECHO,INPUT);

  cameraInit();
  connectAWS();
}

void loop() {
  if(!client.connected()){
    connectAWS();
  }
  client.loop();
  
  digitalWrite(TRIG, LOW); //sensör pasif hale getirildi
  delayMicroseconds(5);
  digitalWrite(TRIG, HIGH); //Sensore ses dalgasının üretmesi için emir verildi
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW); //Yeni dalgaların üretilmemesi için trig pini LOW konumuna getirildi

  sure = pulseIn(ECHO, HIGH); //ses dalgasının geri dönmesi için geçen sure ölçülüyor
  uzaklik = sure / 29.1 / 2;
  if(shouldGrabImage && uzaklik <= 20){
    grabImage();
    shouldGrabImage = false;
  }else if(uzaklik >= 150){
    shouldGrabImage = true;
  }

  Serial.println(uzaklik);
  delay(250);

}


