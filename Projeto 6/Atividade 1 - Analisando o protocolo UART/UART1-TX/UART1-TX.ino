void setup() {
  Serial1.begin(9600,SERIAL_8O2);  
  Serial.begin(9600);
}

void loop() {
 test_write();
}

void test_write() {
    Serial1.write("Cam-Fisica\n");
    Serial.write("Cam-Fisica\n");
    delay(10);
}

void test_receive() {
}
