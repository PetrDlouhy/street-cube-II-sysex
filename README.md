# BOSS CUBE Street II SysEx MIDI Messages

This repository contains information about BOSS CUBE Street II SysEx MIDI messages reverse-engineered from the BOSS CUBE Street II editor app.

## Reverse Engineering Method

The method used to extract these codes:

1. **Android Setup**: In Android Developer options, enable `Enable Bluetooth HCI snoop log`
2. **Recording**: Record actions in the Boss app while tracking them and marking with known actions (e.g., adjusting master out volume)
3. **Log Generation**: Generate bugreport via USB with `adb bugreport cube_log`
4. **Log Extraction**: Extract `/data/log/btsnoop_hci.log` from the generated .zip file
5. **Data Processing**: Extract relevant communication with:
   - `tshark -r btsnoop_hci.log --hexdump ascii > dump.hex`
   - `cat dump.hex | grep "f0 41" -A 1 | grep "^0010" | vim -`
6. **Analysis**: Analyze the `f0 41` codes (without the initial `f0 41`) and map to known app actions

## Usage with MIDI Commander

The SysEx messages work with apps like [MIDI Commander](https://www.bordero.it/Apps/MidiCommander/) by setting values such as:
```
41 10 00 00 00 00 09 12 20 00 00 04 %V
```

**Important:** MIDI Commander automatically adds the `F0` start byte and `F7` end byte, so you only enter the middle portion.

## SysEx Message Format

All commands use the following format:
```
F0 41 10 00 00 00 00 09 [CMD] [ADDRESS] [VALUE] [CHECKSUM] F7
```

**Common Elements:**
- `F0` - SysEx start marker
- `41 10 00 00 00 00 09` - Fixed prefix
- `[CMD]` - Command type (`11` = READ, `12` = SET)
- `[ADDRESS]` - Parameter address (3-4 bytes)
- `[VALUE]` - Parameter value (1-2 bytes)
- `[CHECKSUM]` - Roland checksum
- `F7` - SysEx end marker

**Legend:**
- **vv** - The selected value (1 or 2 bytes), with HEX range in parentheses
- **cc** - Roland checksum

## Parameter Reference

### Global Settings (00 00 00 xx)

| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 00 00 00 04 | Footswitch 1 Tip | 00-05 | 00=Off, 01=Guitar Effect, 02=Mic/Inst Effect, 03=Delay, 04=Reverb, 05=Looper |
| 00 00 00 05 | Footswitch 1 Ring | 00-05 | Same as above |
| 00 00 00 06 | Footswitch 2 Tip | 00-05 | Same as above |
| 00 00 00 07 | Footswitch 2 Ring | 00-05 | Same as above |
| 00 00 00 0A | Looper Rec Time | 00-01 | 00=Normal, 01=Long |
| 00 00 00 0B | Looper Mic/Inst Assign | 00-01 | 00=Off, 01=On |
| 00 00 00 0C | Looper Guitar/Mic Assign | 00-01 | 00=Off, 01=On |
| 00 00 00 0D | Looper Reverb Assign | 00-01 | 00=Off, 01=On |
| 00 00 00 0E | Looper I-Cube Link/Aux/BT Assign | 00-01 | 00=Off, 01=On |
| 00 00 00 10 | I-Cube Link Loopback | 00-01 | 00=Off, 01=On |
| 00 00 00 17 | USB Audio Loopback | 00-01 | 00=Off, 01=On |

### Effects & Instruments (10 00 00 xx)

#### General
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 00 | Mic/Inst EQ Type | 00-03 | [Type 1, Type 2, Type 3, Type 4] |
| 10 00 00 01 | Mic/Inst Effect Type | 00-05 | 00=Harmony, 01=Chorus, 02=Phaser, 03=Flanger, 04=Tremolo, 05=T.WAH |

#### Mic/Inst Harmony
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 0B | Key | 00-01 | 00=Auto, 01=Set |
| 10 00 00 0C | Key Setup | 00-0B | [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B] |
| 10 00 00 0D | Accurate | 00-09 | 1-10 |
| 10 00 00 0E | Voice Assign | 00-03 | 00=Default, 01=Unison/Low/High, 02=Unison/Low/Higher, 03=Low/High/Higher |

#### Mic/Inst Chorus
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 08 | Low Rate | 00-64 | 0-100 |
| 10 00 00 09 | Low Depth | 00-64 | 0-100 |
| 10 00 00 0A | Low Pre Delay | 00-64 | 0-100 |
| 10 00 00 0B | Low Level | 00-64 | 0-100 |
| 10 00 00 0C | Direct Mix | 00-64 | 0-100 |
| 10 00 00 0D | High Rate | 00-64 | 0-100 |
| 10 00 00 0E | High Depth | 00-64 | 0-100 |
| 10 00 00 0F | High Pre Delay | 00-64 | 0-100 |
| 10 00 00 10 | High Level | 00-64 | 0-100 |
| 10 00 00 11 | Xover Freq | 00-10 | [200Hz, 250Hz, 315Hz, 400Hz, 500Hz, 630Hz, 800Hz, 1.0kHz, 1.25kHz, 1.6kHz, 2.0kHz, 2.5kHz, 3.15kHz, 4.0kHz, 5.0kHz, 6.3kHz, 8.0kHz] |

#### Mic/Inst Phaser
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 13 | Type | 00-03 | [4stage, 8stage, 12stage, BiPHASE] |
| 10 00 00 14 | Rate | 00-64 | 0-100 |
| 10 00 00 15 | Depth | 00-64 | 0-100 |
| 10 00 00 16 | Resonance | 00-64 | 0-100 |
| 10 00 00 17 | Manual | 00-64 | 0-100 |
| 10 00 00 18 | Level | 00-64 | 0-100 |

#### Mic/Inst Flanger
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 1A | Rate | 00-64 | 0-100 |
| 10 00 00 1B | Depth | 00-64 | 0-100 |
| 10 00 00 1C | Resonance | 00-64 | 0-100 |
| 10 00 00 1D | Manual | 00-64 | 0-100 |
| 10 00 00 1E | Level | 00-64 | 0-100 |
| 10 00 00 1F | Low Cut | 00-0A | [FLAT, 55Hz, 110Hz, 165Hz, 200Hz, 280Hz, 340Hz, 400Hz, 500Hz, 530Hz, 800Hz] |

#### Mic/Inst Tremolo
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 21 | Wave Shape | 00-64 | 0-100 |
| 10 00 00 22 | Rate | 00-64 | 0-100 |
| 10 00 00 23 | Depth | 00-64 | 0-100 |
| 10 00 00 24 | Level | 00-64 | 0-100 |

#### Mic/Inst T.WAH
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 26 | Mode | 00-01 | 00=LPF, 01=BPF |
| 10 00 00 27 | Polarity | 00-01 | 00=UP, 01=DOWN |
| 10 00 00 28 | Sens | 00-64 | 0-100 |
| 10 00 00 29 | Frequency | 00-64 | 0-100 |
| 10 00 00 2A | Peak | 00-64 | 0-100 |
| 10 00 00 2B | Level | 00-64 | 0-100 |

#### Reverb
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 2D | Type | 00-02 | [ROOM, HALL, PLATE] |
| 10 00 00 2E | Time | 00-31 | 0.1s-5.0s (0.1s steps) |
| 10 00 00 2F | Pre-Delay | 00 00-01 48 | 0-200ms (16-bit value) |
| 10 00 00 31 | Mic/Inst Effect Level | 00-64 | 0-100 |
| 10 00 00 32 | Low Cut | 00-0C | Frequency in Hz |
| 10 00 00 33 | High Cut | 00-0A | Frequency in Hz |
| 10 00 00 34 | Density | 00-0A | 0-10 |
| 10 00 00 35 | Knob Assign | 00-01 | 00=Rev Time, 01=FX Level |

#### Guitar Amp
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 36 | Clean Type | 00-01 | 0-1 |
| 10 00 00 37 | Crunch Type | 00-01 | 0-1 |
| 10 00 00 38 | Lead Type | 00-01 | 0-1 |
| 10 00 00 39 | Effect Type | 00-04 | 00=Chorus, 01=Phaser, 02=Flanger, 03=Tremolo, 04=T.WAH |

#### Guitar Chorus
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 3B | Low Rate | 00-64 | 0-100 |
| 10 00 00 3C | Low Depth | 00-64 | 0-100 |
| 10 00 00 3D | Low Pre Delay | 00-64 | 0-100 |
| 10 00 00 3E | Low Level | 00-64 | 0-100 |
| 10 00 00 3F | Direct Mix | 00-64 | 0-100 |
| 10 00 00 40 | High Rate | 00-64 | 0-100 |
| 10 00 00 41 | High Depth | 00-64 | 0-100 |
| 10 00 00 42 | High Pre Delay | 00-64 | 0-100 |
| 10 00 00 43 | High Level | 00-64 | 0-100 |
| 10 00 00 44 | Xover Freq | 00-10 | Same as Mic/Inst Chorus |

#### Guitar Phaser
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 46 | Type | 00-03 | [4stage, 8stage, 12stage, BiPHASE] |
| 10 00 00 47 | Rate | 00-64 | 0-100 |
| 10 00 00 48 | Depth | 00-64 | 0-100 |
| 10 00 00 49 | Resonance | 00-64 | 0-100 |
| 10 00 00 4A | Manual | 00-64 | 0-100 |
| 10 00 00 4B | Level | 00-64 | 0-100 |

#### Guitar Flanger
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 4D | Rate | 00-64 | 0-100 |
| 10 00 00 4E | Depth | 00-64 | 0-100 |
| 10 00 00 4F | Resonance | 00-64 | 0-100 |
| 10 00 00 50 | Manual | 00-64 | 0-100 |
| 10 00 00 51 | Level | 00-64 | 0-100 |
| 10 00 00 52 | Low Cut | 00-0A | Same as Mic/Inst Flanger |

#### Guitar Tremolo
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 54 | Wave Shape | 00-64 | 0-100 |
| 10 00 00 55 | Rate | 00-64 | 0-100 |
| 10 00 00 56 | Depth | 00-64 | 0-100 |
| 10 00 00 57 | Level | 00-64 | 0-100 |

#### Guitar T.WAH
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 59 | Mode | 00-01 | 00=LPF, 01=BPF |
| 10 00 00 5A | Polarity | 00-01 | 00=UP, 01=DOWN |
| 10 00 00 5B | Sens | 00-64 | 0-100 |
| 10 00 00 5C | Frequency | 00-64 | 0-100 |
| 10 00 00 5D | Peak | 00-64 | 0-100 |
| 10 00 00 5E | Level | 00-64 | 0-100 |

#### Guitar Delay
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 60 | Type | 00-03 | [Digital, Reverse, Analog, Tape Echo] |
| 10 00 00 61 | Time | 00 00-07 47 | 0-1500ms (16-bit value) |
| 10 00 00 63 | Feedback | 00-64 | 0-100 |
| 10 00 00 64 | High Cut | 00-0E | Frequency |
| 10 00 00 65 | Effect Level | 00-64 | 0-100 |
| 10 00 00 66 | Knob Assign | 00-03 | Function assignment |

#### Additional
| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 10 00 00 67 | Guitar Reverb Effect Level | 00-64 | 0-100 |
| 10 00 00 68 | Tuner Pitch | 00-64 | Pitch adjustment |

### Mixer (20 00 00 xx)

| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 20 00 00 00 | Mic/Instrument Volume | 00-64 | 0-100 |
| 20 00 00 01 | Guitar/Mic Volume | 00-64 | 0-100 |
| 20 00 00 02 | I-Cube Link/Aux/BT Volume | 00-64 | 0-100 |
| 20 00 00 03 | I-Cube Link Out Volume | 00-64 | 0-100 |
| 20 00 00 04 | Master Out Volume | 00-64 | 0-100 |

### System Commands (7F xx xx xx)

| Address&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Parameter | Range | Values/Notes |
|---------|-----------|-------|--------------|
| 7F 00 00 01 | Notification Control | 00-01 | 00=Disable, 01=Enable continuous notifications |
| 7F 00 00 02 | Tuner Control | 00-01 | 00=Off, 01=On |
| 7F 01 01 03 | Delay TAP | Variable | TAP tempo function |
| 7F 01 02 04 | Effect Activation | 7F 7F | Apply changes command |

## Usage Examples

### Basic Parameter Control
```
# Complete SysEx format:
F0 41 10 00 00 00 00 09 12 20 00 00 04 32 2C F7    # Set master volume to 50
F0 41 10 00 00 00 00 09 12 10 00 00 01 02 7D F7    # Switch to Phaser effect
```

### Reading Parameters

Reading works by sending a request with command `11` and the Boss Cube responds with command `12` containing the current value.

#### Read Request Format
```
# Complete SysEx format (request):
F0 41 10 00 00 00 00 09 11 20 00 00 04 00 00 00 01 5B F7    # Read master volume
```

#### Response Format
The Boss Cube responds immediately with the current value:
```
# Boss Cube response (complete SysEx):
F0 41 10 00 00 00 00 09 12 20 00 00 04 32 2C F7            # Master volume is 50 (0x32)

# Response breakdown:
# F0                        - SysEx start
# 41 10 00 00 00 00 09      - Roland header  
# 12                        - Data response (not 11!)
# 20 00 00 04               - Address (master volume)
# 32                        - Current value (50 decimal)
# 2C                        - Checksum
# F7                        - SysEx end
```

#### Read Request Breakdown
```
# Read request breakdown:
# F0                        - SysEx start
# 41 10 00 00 00 00 09      - Roland header
# 11                        - Read command (not 12!)
# 20 00 00 04               - Address to read from
# 00 00 00 01               - Read length (1 byte)
# 5B                        - Checksum
# F7                        - SysEx end
```

### System Initialization
```
# Complete SysEx format:
F0 41 10 00 00 00 00 09 12 7F 00 00 01 01 7F F7    # Enable notifications
```

## Tools and Resources

- **MIDI Commander**: Recommended app for sending SysEx commands
- **SysEx Format**: All commands use Roland standard format with checksum
- **Bluetooth HCI**: Method used to reverse-engineer these commands
- **Checksum**: Roland standard - sum of address and data bytes, then 128 minus result
- **SysEx Tutorial**: [Comprehensive SysEx guide](https://www.2writers.com/eddie/TutSysEx.htm) explaining Roland checksum calculation

## 🎛️ Live Web Implementation

**[Boss Cube Web Control](https://github.com/PetrDlouhy/boss-web-control)** - A complete Progressive Web App that puts these SysEx commands into action!

**✨ What it does:**
- 🔥 **Complete Boss Cube II control** via Web Bluetooth - no cables needed!
- 🎚️ **Full mixer interface** - Master, Mic/Inst, Guitar, Aux volumes in real-time
- 🎸 **All effects controls** - Reverb, Chorus, Phaser, Tremolo, T.WAH with automatic switching
- 🦶 **EV-1-WL pedal support** - Control any parameter with expression pedal + footswitches
- 📱 **Mobile-ready PWA** - Install on phone/tablet for stage use
- ⚡ **Instant sync** - UI updates live as you turn physical knobs

**🚀 Why it's awesome:**
- **Better than Boss Tone Studio** - Direct Bluetooth connection, no USB required
- **Stage-ready interface** - Designed for live performance with clear visual feedback  
- **Dual Bluetooth** - Connect Boss Cube + EV-1-WL pedal simultaneously
- **Open source** - Built using the SysEx commands documented in this repository

**Perfect for musicians who want wireless control of their Boss Cube II without the limitations of the official app!**

## Reading Multiple Parameters

When reading multiple parameters, add small delays (100-150ms) between requests to avoid overwhelming the Boss Cube.

#### Example: Reading All Mixer Values
```
# Send these read requests with 100ms delays between each:

→ F0 41 10 00 00 00 00 09 11 20 00 00 00 00 00 00 01 5F F7    # Read Mic/Inst volume
← F0 41 10 00 00 00 00 09 12 20 00 00 00 32 2D F7            # Response: 50

→ F0 41 10 00 00 00 00 09 11 20 00 00 01 00 00 00 01 5E F7    # Read Guitar/Mic volume  
← F0 41 10 00 00 00 00 09 12 20 00 00 01 28 37 F7            # Response: 40

→ F0 41 10 00 00 00 00 09 11 20 00 00 02 00 00 00 01 5D F7    # Read I-Cube Link/Aux/BT
← F0 41 10 00 00 00 00 09 12 20 00 00 02 1E 41 F7            # Response: 30

→ F0 41 10 00 00 00 00 09 11 20 00 00 04 00 00 00 01 5B F7    # Read Master volume
← F0 41 10 00 00 00 00 09 12 20 00 00 04 46 19 F7            # Response: 70
```

## Physical Knob vs Read Response Detection

The Boss Cube sends identical format messages for both read responses and physical knob changes. To distinguish them:

#### Read Response Example
```
→ F0 41 10 00 00 00 00 09 11 20 00 00 04 00 00 00 01 5B F7    # Send read request
← F0 41 10 00 00 00 00 09 12 20 00 00 04 32 2C F7            # Response arrives ~50ms later
```

#### Physical Knob Change Example  
```
# No read request sent, but Boss Cube spontaneously reports:
← F0 41 10 00 00 00 00 09 12 20 00 00 04 3C 22 F7            # Master volume changed to 60
```

**Detection Strategy:**
- Track timestamps when you send read requests
- If response arrives within 2 seconds of a read request to same address → read response
- If no recent read request for that address → physical knob change

## Notes

- 16-bit values (like delay time) use two consecutive bytes
- Enable notifications (7F 00 00 01 = 01) to receive real-time updates
- Effect switching may require activation command (7F 01 02 04) to take effect
- Some addresses may have additional undocumented functions
- **Important**: Boss Cube doesn't check the checksum (tested on master out and other commands), but requires exact GATT message format including timestamp before final F7
- Add 100-150ms delays between read requests to avoid overwhelming the device
- Read responses and physical knob changes use identical message format - distinguish by timing
