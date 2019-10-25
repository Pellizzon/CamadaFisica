
void setup() {
   Serial1.begin(9600,SERIAL_8E1);  
}

void loop() {
 test_write();
}

void test_write() {
    Serial1.write("a");
    delay(1000);
}
