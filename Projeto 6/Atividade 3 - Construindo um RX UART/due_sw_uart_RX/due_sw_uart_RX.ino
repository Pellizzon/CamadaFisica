#include "sw_uart.h"

due_sw_uart uart;

void setup() {
  Serial.begin(115200);
  sw_uart_setup(&uart, 4, 3, 1, 8, SW_UART_EVEN_PARITY, 20000);
}

void loop() {
 receive_byte();
 delay(5);
}



void receive_byte() {
  char data;
  int code = sw_uart_receive_byte(&uart, &data);
  if(code == SW_UART_SUCCESS) {
     Serial.println(data);
  } else if(code == SW_UART_ERROR_PARITY) {
    Serial.println("\nPARITY ERROR");
  } else {
    Serial.println("\nOTHER");
    Serial.print(code);
  }
}
