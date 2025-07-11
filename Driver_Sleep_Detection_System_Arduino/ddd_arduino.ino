#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

int ledPin = 9;
int buzzerPin = 6;
char input;

unsigned long lastAlertTime = 0;
int alertCount = 0;

void setup() {
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("System Ready");

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    input = Serial.read();

    if (input == 'a') {
      lcd.setCursor(0, 1);
      lcd.print("ALERT: Drowsy   ");
      digitalWrite(ledPin, HIGH);
      digitalWrite(buzzerPin, HIGH);

      unsigned long currentTime = millis();

      // Reset counter if time exceeded
      if (currentTime - lastAlertTime > 15000) {
        alertCount = 1;
      } else {
        alertCount++;
      }

      lastAlertTime = currentTime;

      // Show break suggestion
      if (alertCount >= 3) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Take a Break!");
        digitalWrite(ledPin, HIGH);
        digitalWrite(buzzerPin, HIGH);
        delay(4000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("System Ready");
        alertCount = 0;
      }
    }

    else if (input == 'b') {
      lcd.setCursor(0, 1);
      lcd.print("Status: Active  ");
      digitalWrite(ledPin, LOW);
      digitalWrite(buzzerPin, LOW);
    }
  }
}
