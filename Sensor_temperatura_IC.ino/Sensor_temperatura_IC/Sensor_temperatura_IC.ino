#define reset_timer() ticks = millis()
#define get_timer() (millis() - ticks)

#define FASTADC 1
#define SENSOR_QUANTITY 2
#define RESISTENCIA 10 //https://www.mouser.com/ProductDetail/Ohmite/TNP10SC10R0FE?qs=tucQmhgEO3o205v23Kjs9w%3D%3D

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
// Declaracao das variaveis
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
static uint32_t ticks = 0;
int option = 0;
bool start = false;

bool start_command = false;  // Verdadeiro se comecar a leitura do sensor
static uint32_t potencia = 0;  // potencia do resistor

float sensor_value[2] = {0, 0};
float Rth = 0;
float pinSensor[2] = {A1, A2};  // Pino do sensor de temperatura
float temperaturas[2] = {0, 0};
float tensao = 0;

int potenciaPin = 6;
int potenciaPWM = 0;

//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// Seta os pinos e a leitura serial
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
void setup() {
    // set prescale to 16
    sbi(ADCSRA, ADPS2);
    cbi(ADCSRA, ADPS1);
    cbi(ADCSRA, ADPS0);

    pinMode(potenciaPin, OUTPUT);

    Serial.begin(115200);                // Baund Rate da leitura serial
}
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// Comeca o loop da funcao principal
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
void loop() {
    if (Serial.available()){  // Caso a serial estiver diponivel chamar a funcao `parse_serial()
        parse_serial();
    }

    if (start_command) {  // Entra no `if` caso o `start_command` for `True`
        reset_timer();    // Reseta o timer
        
        for (int temp_sensors = 0; temp_sensors < SENSOR_QUANTITY; temp_sensors++) {
                // Leitura analogica do sensor de gas
                temperaturas[temp_sensors] = analogRead(pinSensor[temp_sensors]);
            }
       
        if (potencia > 0 && potencia <= 10){
            Rth = (abs(temperaturas[0]-temperaturas[1])/potencia);
            tensao = sqrt(RESISTENCIA*potencia); //Resitencia 10 Ohm, Potencia maxima 10 Watt
            potenciaPWM = map(tensao, 0, 10, 0, 255);
            analogWrite(potenciaPin, potenciaPWM); //Manda pro arduino PWM para cotrolar potencia do resistor
          }else{
            Rth = -1;
            }
          
        sendToPython(&Rth);  // Envia o valor em PPM para a funcao `sendToPython`
    }
}
//----------------------------------------------------------------------------------------------------------------

// Funcoes
//---------------------------------------------------------------------------------------------------------------
// Recebe o valor em `data` e converte este valor em binario

void sendToPython(float* data){ // Adicionar mais sensores  `double* data2`               
  byte* byteData = (byte*)(data);       // Sensor 1

  byte buf[4] = {byteData[0], byteData[1], byteData[2], byteData[3]};

  Serial.write(buf, 4);      // Buffer de x = 4(bytes) * Numero de sensores
}
// Recebe os dados do Python
void parse_serial() {
    if (Serial.available() < 11) {  // Verifica se o valor e menor que 11 caracteres
        return;
    }

    String command = Serial.readStringUntil('\n');  // Faz a leitura seria recebida do Python
    command.trim();

    uint32_t value =
        command.substring(4, 9).toInt();  // Armazena em value a substring entre 4,9 do valor recebido do python

    switch (command[2]) {  // Casos variados da string na posicao 2
        case 'o': {
            option = value;
            break;
        }

        case 'p': {
            potencia = value;
            break;
        }

        case 's': {
            start_command = true;  // Inicia a leitura PPM no loop principal
            break;
        }
    }
}
