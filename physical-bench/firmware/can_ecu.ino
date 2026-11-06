/* ECU sender + status: STM32 Nucleo-L476RG + MCP2515 (8 MHz), CS=D10, 500 kbit/s.
 * Sends 0x100/0x120/0x188/0x300; prints begin rc, TEC and EFLG on the ST-Link VCP each second.
 * begin rc=0 means SPI/MCP2515 reachable; TEC staying low and EFLG=0 means frames are being ACKed.
 */
#include <mcp_can.h>
#include <SPI.h>

MCP_CAN mcp(D10);
#define CSPIN D10
SPISettings spicfg(1000000, MSBFIRST, SPI_MODE0);

byte rd(byte a) {
  SPI.beginTransaction(spicfg);
  digitalWrite(CSPIN, LOW);
  SPI.transfer(0x03); SPI.transfer(a);
  byte v = SPI.transfer(0x00);
  digitalWrite(CSPIN, HIGH);
  SPI.endTransaction();
  return v;
}

bool ok = false;

void setup() {
  Serial.begin(115200);
  SPI.setMOSI(PA7); SPI.setMISO(PA6); SPI.setSCLK(PA5);
  delay(300);
  byte r = mcp.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ);
  Serial.print("begin rc="); Serial.println(r);
  if (r == CAN_OK) { ok = true; mcp.setMode(MCP_NORMAL); Serial.println("NORMAL @500k"); }
  else Serial.println("begin FAILED (SPI/level problem)");
}

unsigned long t100 = 0, t120 = 0, t188 = 0, t300 = 0, tp = 0;
byte lastRes = 0;
unsigned int ctr = 0;   // 16-bit counter in bytes 2-3 of 0x100 (like the synthetic schema)
unsigned long rxTotal = 0, rxSpoof = 0, rxOther = 0;  // frames RECEIVED from other nodes (victim-ECU view)

void loop() {
  if (!ok) { Serial.println("begin FAILED (SPI nao responde)"); delay(1000); return; }
  while (mcp.checkReceive() == CAN_MSGAVAIL) {
    unsigned long rid; byte rlen; byte rbuf[8];
    mcp.readMsgBuf(&rid, &rlen, rbuf);
    rxTotal++;
    if (rid == 0x100 && rlen > 0 && rbuf[0] >= 130) rxSpoof++;
    else if (rid != 0x100 && rid != 0x120 && rid != 0x188 && rid != 0x300) rxOther++;
  }
  unsigned long n = millis();
  // speed (km/h) is byte 0, as the evidence pipeline decodes 0x100; baseline ~27..92
  // smooth speed profile (run B): 60 +/- 32 km/h sinusoid (period ~21 s) plus +/-1 km/h noise, like the synthetic baseline
  byte spdv = (byte)(60.0f + 32.0f * sinf(millis() * 0.0003f) + (float)random(-1, 2));
  byte d100[8] = {spdv, 0x00, (byte)(ctr & 0xFF), (byte)(ctr >> 8), 0x26, 0x56, 0x4B, 0x00};
  byte d[8]    = {0, 0, 0, 0, 0, 0, 0, 0};
  if (n - t100 >= 20)  { t100 = n; lastRes = mcp.sendMsgBuf(0x100, 0, 8, d100); ctr++; }
  if (n - t120 >= 50)  { t120 = n; mcp.sendMsgBuf(0x120, 0, 8, d); }
  if (n - t188 >= 100) { t188 = n; mcp.sendMsgBuf(0x188, 0, 8, d); }
  if (n - t300 >= 200) { t300 = n; mcp.sendMsgBuf(0x300, 0, 8, d); }
  if (n - tp >= 1000) {
    tp = n;
    Serial.print("send="); Serial.print(lastRes);
    Serial.print(" TEC="); Serial.print(rd(0x1C));
    Serial.print(" EFLG=0x"); Serial.print(rd(0x2D), HEX);
    Serial.print(" rx="); Serial.print(rxTotal);
    Serial.print(" spoof="); Serial.print(rxSpoof);
    Serial.print(" other="); Serial.println(rxOther);
  }
}
