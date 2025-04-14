# SECCON Glitch Gate

SECCON Glitch Gate is a hardware challenge.
You need to analyze the behavior of an embedded system and exploit it to retrieve hidden flags.
**The challenge includes two flags.**

## Setup

The challenge involves two Arduino boards: one as the attacker and one as the victim.
The victim Arduino and an oscilloscope are set up in a separate room.
You must complete your exploit beforehand and then reserve a slot via a designated website to access the separate room for testing.

The victim's firmware is provided in ELF format. (`seccon_glitch_gate.ino_redacted_wSymbol.elf`)
The two challenge flags are redacted in the distributed firmware files, but the real flags are present on the victim device.

You are allowed to flash and debug the provided firmware on the attacker Arduino for testing.
You can use the following commands to flash the provided firmware onto an Arduino:

```
avr-objcopy -O ihex seccon_glitch_gate.ino_redacted_wSymbol.elf output.hex
avrdude -C[AVRDUDE_CONF] -v -patmega328p -carduino -P[SERIAL_PORT] -b 115200 -D -U flash:w:output.hex:i
```

## Provided tools

**Tools distributed to each team:**

- Arduino nano (for debug and exploit)
- 170-point breadboard
- XY-MOS Power MOSFET module
- USB A to C cable
- Jumper wire F/M x4
- Jumper wire M/M x4
- Precision screwdriver

**Tools in the challenge room:**

- Arduino nano (R/W disabled)
- 170-point breadboard
- USB A to C cable
- USB tester
- USB extension cable (w/0.9A PPTC fuse)
- OWON  SDS1104 Oscilloscope

## Rules

- You may not remove the polyimide tape (Kapton tape) from the Arduino Nano. This tape is in place to prevent accidental damage to the device.
- Only attacks using header pins are allowed. Directly attacking the microcontroller's pins is prohibited.
- Attempting to write to or extract the program from the victim Arduino is prohibited.
- Each attempt in the separate room lasts 20 minutes.
- You can attempt the challenge once a day. (Up to 2 attempts over 2 days)
- When your reserved time begins, at least 1 and up to 4 team members must go to the designated challenge room.
- You may leave the room and give up your attempt at any time.
- You will have access to the victim Arduino and an oscilloscope inside the room.
- Bringing any additional equipment other than your laptop, phones, and the provided tools is strictly prohibited.
- You must follow the instructions given by the event staff at all times.
