const uint16_t WAIT = 0xF00D;
volatile uint16_t continueLoop = 0xCAFE;
const volatile uint8_t key = 0xBE;

uint8_t auth() {
  const uint8_t data = (PIND & 0xE0) | (PINB & 0x1F);
  return (data ^ key) == 0x63;
}

void setup() {
  Serial.begin(38400);
  while (!Serial);

  for (uint8_t i = 5; i < 13; i++)
    pinMode(i, INPUT_PULLUP);

  Serial.println();
  Serial.println( F("====================================================") );
  Serial.println( F("|                                                   |") );  
  Serial.println( F("|                SECCON Glitch Gate                 |") );
  Serial.println( F("|                                                   |") );
  Serial.println( F("====================================================") );
  delay(1000);
  Serial.println( F("[*] Welcome to the SECCON Glitch Gate!") );
  Serial.println( F("[*] Initializing system...") );

  delay(1000);
  if (auth())
    Serial.println( F("[+] The hardware configuration is correct. The first flag: SECCON{Two_wires_swap_two_bits}") );
  else
    Serial.println( F("[!] ERROR: Incorrect hardware configuration detected. No flag for you!") );
  delay(3000);
  Serial.println();
}

void loop() {
  while (continueLoop) {
    volatile uint16_t charge = 0;

    Serial.print("[*] Gathering inner strength");
    for (uint8_t i = 0; i < 24; i++) {
      for (volatile uint16_t j = 0; j < WAIT; j++);
      charge++;
      Serial.print(".");
      continueLoop = (charge <= 0xFF);
      if (!continueLoop) break;
    }
    Serial.println();

    if (continueLoop)
      Serial.println("[-] You lack discipline! No flag for you!");
  }

  Serial.println("[+] The second flag: SECCON{You_have_mastered_the_art_of_fault_injection!}");
  while(1);
}
