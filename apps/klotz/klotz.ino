int pinX[] = {4,5,6,7};
int pinY[] = {8,9,10,11};

void setup() {
	Serial.begin(9600);

	for(int idx = 0; idx < 4; idx++) {
		pinMode(pinX[idx], INPUT);
		pinMode(pinY[idx], INPUT_PULLUP);
	}
	
}

void loop() {
	checkMatrix();
}

void checkMatrix(){
	for(int idxX = 0; idxX < 4; idxX++) {
		pinMode(pinX[idxX], OUTPUT);
		for(int idxY = 0; idxY < 4; idxY++) {
			if (!digitalRead(pinY[idxY]))
			{
				send(idxX, idxY);
				delay(100);
				while(!digitalRead(pinY[idxY])){delay(5);}
				delay(100);
			}
		}
		pinMode(pinX[idxX], INPUT);
	}	
}


void send(int idxX, int idxY){
	Serial.print(idxX);
	Serial.print(",");
	Serial.println(idxY);
}
