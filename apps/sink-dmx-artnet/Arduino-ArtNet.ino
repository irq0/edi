/*
This is a basic example that will print out the header and the content of an ArtDmx packet.
This example uses the read() function and the different getter functions to read the data.
This example may be copied under the terms of the MIT license, see the LICENSE file for details

This example has been modified and extended:
- forward incoming data to DMX
- use DHCP
*/

#include <Artnet.h>
#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>
#include <DMXSerial.h>

#ifndef DMX_USE_PORT1
#error Please define DMX_USE_PORT1 in DMXSerial.h!
#endif

Artnet artnet;

// Change ip and mac address for your setup
byte ip[] = {192, 168, 2, 2};
byte mac[] = {0x04, 0xE9, 0xE5, 0x00, 0x69, 0xEC};
// 90-A2-DA-00-7B-62

void setup()
{
  Serial.begin(115200);
  Serial.println("initializing...");
  Ethernet.begin(mac);
  ip[0] = Ethernet.localIP()[0];
  ip[1] = Ethernet.localIP()[1];
  ip[2] = Ethernet.localIP()[2];
  ip[3] = Ethernet.localIP()[3];
  artnet.begin(mac, ip);
  Serial.println(Ethernet.localIP());

  DMXSerial.init(DMXController, 22);
}

void loop()
{
  if (artnet.read() == ART_DMX)
  {
    // print out our data
    Serial.print("universe number = ");
    Serial.print(artnet.getUniverse());
    Serial.print("\tdata length = ");
    Serial.print(artnet.getLength());
    Serial.print("\tsequence n0. = ");
    Serial.println(artnet.getSequence());
    Serial.print("DMX data: ");
    for (int i = 0 ; i < artnet.getLength() && i < 50 ; i++)
    {
      Serial.print(artnet.getDmxFrame()[i]);
      Serial.print("  ");
    }
    Serial.println();
    Serial.println();

    if (artnet.getUniverse() == 0 || artnet.getUniverse() == 145) {
      for (int i=0;i<512 && i < artnet.getLength();i++) {
        DMXSerial.write(i, artnet.getDmxFrame()[i]);
      }
    }
  }
}
