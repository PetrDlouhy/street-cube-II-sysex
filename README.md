This repository contains information about BOSS CUBE Street II SysEx MIDI messages

I reverse ingenierred the messages send by BOSS CUBE Street II editor app.
The list is yet quite incomplete and not all possibilities of SysEx MIDI are yet explored.

These codes can be directly used in apps such as [Midi commander](https://www.bordero.it/Apps/MidiCommander/) (which is more flexible than the original app and can send SysEx codes in correct format including the checksum).
I would also like to create some physical controls for my CUBE in the future.

The method I used to extract these codes:

1. In Android Developer options I turnned on `Enable Bluetooth HCI snoop log`
2. I recorded some actions in the Boss app while keeping track of them and marking them with known actions (such as adjusting master out volume).
3. Through USB I generated bugreport with `adb bugreport cube_log`
4. From the generated .zip file I extracted `/data/log/btsnoop_hci.log`
5. I extracted the relevant comunication with `tshark -r btsnoop_hci.log --hexdump ascii   > dump.hex` and `cat dump.hex | grep "f0 41" -A 1 | grep "^0010" | vim -`
6. Now I had the `f0 41` codes each on one line (without the initial `f0 41`). I assumed what was happening according to what I was previously doing in the app.

Usage with MIDI Commander:

The control works when I set the SysEx in Midi Commander to values such as F0 `41 10 00 00 00 00 09 12 20 00 00 04 %V` F7


Resources:

- https://www.2writers.com/eddie/TutSysEx.htm


Here are the messages deciphered so far:

legend:

- **vv** The selected value (1 or 2 bytes). The HEX range of the value is in parantheses.
- **cc** Roland checksum.


# MIXER
```
f0 41 10 00 00 00 00 09 12 20 00 00 00 vv cc f7      # mic/instrument (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 01 vv cc f7      # guitar/mic (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 02 vv cc f7      # i-cube link/aux/bluetooth (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 03 vv cc f7      # i-cube link out (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 04 vv cc f7      # master out (00 - 64)

f0 41 10 00 00 00 00 09 12 00 00 00 10 vv cc f7      # i-cube link loopback (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 17 vv cc f7      # USB Audio loopback (00 - 01)
```

# MIC/INST EQUALIZER
```
f0 41 10 00 00 00 00 09 12 10 00 00 00 vv cc f7      # type (00 - 03)
```



# MIC/INST EFFECT SWITCHING

The Boss Cube Street II supports 6 different Mic/Inst effects that can be switched using commands to address `10 00 00 01`:

```
f0 41 10 00 00 00 00 09 12 10 00 00 01 00 7f f7      # Switch to Harmony
f0 41 10 00 00 00 00 09 12 10 00 00 01 01 7e f7      # Switch to Chorus  
f0 41 10 00 00 00 00 09 12 10 00 00 01 02 7d f7      # Switch to Phaser
f0 41 10 00 00 00 00 09 12 10 00 00 01 03 7c f7      # Switch to Flanger
f0 41 10 00 00 00 00 09 12 10 00 00 01 04 7b f7      # Switch to Tremolo
f0 41 10 00 00 00 00 09 12 10 00 00 01 05 7a f7      # Switch to T.WAH
```

## MIC/INST HARMONY
```
# Note: Harmony effect parameters are unique to MIC/INST and don't have guitar equivalents
f0 41 10 00 00 00 00 09 12 10 00 00 0b vv cc f7      # key (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 0c vv cc f7      # key setup (00 - 0b)
f0 41 10 00 00 00 00 09 12 10 00 00 0d vv cc f7      # accurate (00 - 09)
f0 41 10 00 00 00 00 09 12 10 00 00 0e vv cc f7      # voice assign (00 - 03)
```

## MIC/INST CHORUS
```
f0 41 10 00 00 00 00 09 12 10 00 00 08 vv cc f7      # low rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 09 vv cc f7      # low depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0a vv cc f7      # low pre delay (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0b vv cc f7      # low level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0c vv cc f7      # direct mix (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0d vv cc f7      # high rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0e vv cc f7      # high depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 0f vv cc f7      # high pre delay (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 10 vv cc f7      # high level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 11 vv cc f7      # xover frequency (00 - 10)
```

## MIC/INST PHASER
```
f0 41 10 00 00 00 00 09 12 10 00 00 13 vv cc f7      # type (00 - 03)
f0 41 10 00 00 00 00 09 12 10 00 00 14 vv cc f7      # rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 15 vv cc f7      # depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 16 vv cc f7      # resonance (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 17 vv cc f7      # manual (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 18 vv cc f7      # level (00 - 64)
```

## MIC/INST FLANGER
```
f0 41 10 00 00 00 00 09 12 10 00 00 1a vv cc f7      # rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 1b vv cc f7      # depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 1c vv cc f7      # resonance (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 1d vv cc f7      # manual (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 1e vv cc f7      # level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 1f vv cc f7      # low cut (00 - 0a)
```

## MIC/INST TREMOLO
```
f0 41 10 00 00 00 00 09 12 10 00 00 21 vv cc f7      # wave shape (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 22 vv cc f7      # rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 23 vv cc f7      # depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 24 vv cc f7      # level (00 - 64)
```

## MIC/INST T.WAH
```
f0 41 10 00 00 00 00 09 12 10 00 00 26 vv cc f7      # mode (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 27 vv cc f7      # polarity (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 28 vv cc f7      # sens (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 29 vv cc f7      # frequency (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2a vv cc f7      # peak (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2b vv cc f7      # level (00 - 64)
```

# MIC/INST REVERB

```
f0 41 10 00 00 00 00 09 12 10 00 00 2d vv cc f7      # reverb type (00 - 02)
f0 41 10 00 00 00 00 09 12 10 00 00 2e vv cc f7      # reverb time s (00 - 31?)
f0 41 10 00 00 00 00 09 12 10 00 00 2f vv vv cc f7   # pre-delay ms (00 00 - 01 48?)
f0 41 10 00 00 00 00 09 12 10 00 00 31 vv cc f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 32 vv cc f7      # low cut Hz (00 - 0c)
f0 41 10 00 00 00 00 09 12 10 00 00 33 vv cc f7      # high cut Hz (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 34 vv cc f7      # density (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 35 vv cc f7      # knob assign function (00 - 01?)
```

# GUITAR DELAY

```
f0 41 10 00 00 00 00 09 12 10 00 00 60 vv cc f7      # Delay type (00 - 03)
f0 41 10 00 00 00 00 09 12 10 00 00 61 vv vv cc f7   # delay time ms (00 00 - 07 47)

f0 41 10 00 00 00 00 09 12 10 00 00 63 vv cc f7      # feedback (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 64 vv cc f7      # high cut (00 - 0E)

f0 41 10 00 00 00 00 09 12 7f 01 01 03 vv cc f7      # TAP?
f0 41 10 00 00 00 00 09 12 7f 01 01 03 vv cc f7

f0 41 10 00 00 00 00 09 12 10 00 00 65 vv cc f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 66 vv cc f7      # Knob asign function (00 - 03)
```

# GUITAR AMP TYPE

```
f0 41 10 00 00 00 00 09 12 10 00 00 36 vv cc f7      # clean (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 37 vv cc f7      # crunch type (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 38 vv cc f7      # lead type (00 - 01)
```

# GUITAR FLANGER
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 02 35 f7      # Switch to flanger
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f7

f0 41 10 00 00 00 00 09 12 10 00 00 4d vv cc f7      # rate
f0 41 10 00 00 00 00 09 12 10 00 00 4e vv cc f7      # depth
f0 41 10 00 00 00 00 09 12 10 00 00 4f vv cc f7      # resonance
f0 41 10 00 00 00 00 09 12 10 00 00 50 vv cc f7      # manual
f0 41 10 00 00 00 00 09 12 10 00 00 51 vv cc f7      # level
f0 41 10 00 00 00 00 09 12 10 00 00 52 vv cc f7      # low cut
```

# GUITAR PHASER
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 01 36 f7      # Switch to phaser
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f7

f0 41 10 00 00 00 00 09 12 10 00 00 47 vv cc f7      # rate
f0 41 10 00 00 00 00 09 12 10 00 00 48 vv cc f7      # depth
f0 41 10 00 00 00 00 09 12 10 00 00 49 vv cc f7      # resonance

f0 41 10 00 00 00 00 09 12 10 00 00 4a vv cc f7      # manual
f0 41 10 00 00 00 00 09 12 10 00 00 4b vv cc f7      # level

f0 41 10 00 00 00 00 09 12 10 00 00 46 vv cc f7      # type (00 - 03)
```

#  GUITAR CHORUS
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 00 37 f7      # Switch to chorus
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f7

f0 41 10 00 00 00 00 09 12 10 00 00 3b vv cc f7      # low rate
f0 41 10 00 00 00 00 09 12 10 00 00 3c vv cc f7      # low depth
f0 41 10 00 00 00 00 09 12 10 00 00 3d vv cc f7      # low pre delay
f0 41 10 00 00 00 00 09 12 10 00 00 3e vv cc f7      # low level
f0 41 10 00 00 00 00 09 12 10 00 00 3f vv cc f7      # direct mix

f0 41 10 00 00 00 00 09 12 10 00 00 40 vv cc f7      # high rate
f0 41 10 00 00 00 00 09 12 10 00 00 41 vv cc f7      # high depth
f0 41 10 00 00 00 00 09 12 10 00 00 42 vv cc f7      # high pre delay
f0 41 10 00 00 00 00 09 12 10 00 00 43 vv cc f7      # high level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 44 vv cc f7      # xover frequency (00 - 10)
```

# GUITAR TREMOLO
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 03 34 f7      # Switch to tremolo
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f7

f0 41 10 00 00 00 00 09 12 10 00 00 54 vv cc f7      # wave shape (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 55 vv cc f7      # rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 56 vv cc f7      # depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 57 vv cc f7      # level (00 - 64)
```

# GUITAR T.WAH
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 04 33 f7      # Switch to T.WAH
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f7

f0 41 10 00 00 00 00 09 12 10 00 00 59 vv cc f7      # Mode (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 5a vv cc f7      # Polarity (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 5b vv cc f7      # Sens (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5c vv cc f7      # Frequency (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5d vv cc f7      # Peak (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5e vv cc f7      # Level (00 - 64)
```

# GUITAR REVERB
```
f0 41 10 00 00 00 00 09 12 10 00 00 2e vv cc f7      # time (s) (00 - 31)
f0 41 10 00 00 00 00 09 12 10 00 00 2f vv vv cc f7   # pre delay (ms) (00 00 - 01 48)
f0 41 10 00 00 00 00 09 12 10 00 00 67 vv cc f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 32 vv cc f7      # low cut (Hz) (00 - 0c)
f0 41 10 00 00 00 00 09 12 10 00 00 33 vv cc f7      # high cut (Hz) (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 34 vv cc f7      # density (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 35 vv cc f7      # knob assign function (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 2d vv cc f7      # type (00 - 02)
```

# FOOT SWITCH CTRL ASSIGN
```
f0 41 10 00 00 00 00 09 12 00 00 00 04 vv cc f7      # sw1-tip (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 05 vv cc f7      # sw1-ring (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 06 vv cc f7      # sw2-tip (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 07 vv cc f7      # sw2-ring (00 - 05)
```

# LOOPER SETTINGS
```
f0 41 10 00 00 00 00 09 12 00 00 00 0a vv cc f7      # Rec time (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0b vv cc f7      # mic/instrument assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0c vv cc f7      # guitar/mic assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0d vv cc f7      # reverb assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0e vv cc f7      # i-cube link/aux/bluetooth assign (00 - 01)
```
# TUNER

```
f0 41 10 00 00 00 00 09 12 7f 00 00 02 vv cc f7      # Tuner on/off (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 68 vv cc f7      # Pitch
```

# NOTIFICATION CONTROL

```
f0 41 10 00 00 00 00 09 12 7f 00 00 01 01 7f f7      # Enable continuous notifications
```

This command enables the Boss Cube to automatically send parameter change notifications when physical knobs are turned. Without this command, the Cube only responds to explicit read requests.

The notification enable register at address `7F 00 00 01`:
- `01` = Enable continuous notifications for physical knob changes
- `00` = Disable continuous notifications (default state)

Once enabled, the Cube will send unsolicited SysEx messages whenever front-panel controls are adjusted, allowing real-time synchronization with editor applications.

# PARAMETER READING

To read current parameter values from the Boss Cube, use READ commands (0x11) instead of SET commands (0x12):

## Basic Parameter Read
```
f0 41 10 00 00 00 00 09 11 aa aa aa aa 00 00 00 01 cc f7
```
Where:
- `11` = READ command (instead of `12` for SET)
- `aa aa aa aa` = Parameter address (same as SET commands)
- `00 00 00 01` = Read length (1 byte)
- `cc` = Roland checksum

## System Initialization Reads
These READ commands help initialize the connection and "prime" the Cube's parameter engine:

```
f0 41 10 00 00 00 00 09 11 7f 00 00 00 00 00 00 01 00 f7    # System Config 1
f0 41 10 00 00 00 00 09 11 7f 00 00 03 00 00 00 01 7d f7    # System Config 2  
f0 41 10 00 00 00 00 09 11 7f 00 00 02 00 00 00 01 7e f7    # System Config 3
f0 41 10 00 00 00 00 09 11 10 00 00 00 00 00 00 01 6f f7    # Guitar Config
f0 41 10 00 00 00 00 09 11 00 00 00 00 00 00 00 01 7f f7    # Global Config
f0 41 10 00 00 00 00 09 11 20 00 00 00 00 00 00 01 5f f7    # Mixer Config 1
f0 41 10 00 00 00 00 09 11 20 00 30 00 00 00 00 01 2f f7    # Mixer Config 2
```

## Example: Reading Master Volume
```
f0 41 10 00 00 00 00 09 11 20 00 00 04 00 00 00 01 5b f7    # Read master volume
```

The Cube responds with the current value using the same address in a SET-format message.

## Notification Maintenance
Some implementations may need periodic maintenance to keep notifications active:
```
# Send the enable command every 5-10 seconds to maintain the notification stream
f0 41 10 00 00 00 00 09 12 7f 00 00 01 01 7f f7      # Periodic notification refresh
```

# UNKNOWN/UNDOCUMENTED COMMANDS

These commands were discovered in the Boss Cube web control application but their exact purpose is not yet fully understood:

## Effect Activation Command (MIC/INST)
```
f0 41 10 00 00 00 00 09 12 7f 01 02 00 7f 7f 00 cc f7    # Effect activation after MIC/INST effect switch
```

**Context:** This command is sent automatically after effect type switching commands (phaser, chorus, tremolo, T.WAH). It appears to be some kind of "effect activation" or "apply changes" command.

**Known usage:**
- Always sent after switching guitar effect types via address `10 00 00 39`
- Uses address `7F 01 02 04` with data `7F 7F`
- May be required to make effect switches take effect
- Checksum: `7C`

**Hypothesis:** This could be a "commit changes" or "effect bank update" command that tells the Cube to apply the new effect configuration.

## Mixer Address Extensions
The web control app also uses additional mixer addresses beyond the documented ones:

```
f0 41 10 00 00 00 00 09 12 20 00 00 05 vv cc f7      # Mixer Address 05 (unknown function)
f0 41 10 00 00 00 00 09 12 20 00 00 06 vv cc f7      # Mixer Address 06 (unknown function)  
f0 41 10 00 00 00 00 09 12 20 00 00 07 vv cc f7      # Mixer Address 07 (unknown function)
f0 41 10 00 00 00 00 09 12 20 00 00 08 vv cc f7      # Mixer Address 08 (unknown function)
f0 41 10 00 00 00 00 09 12 20 00 00 09 vv cc f7      # Mixer Address 09 (unknown function)
f0 41 10 00 00 00 00 09 12 20 00 00 0a vv cc f7      # Mixer Address 0A (unknown function)
```

**Context:** These addresses are in the mixer range (`20 00 00 xx`) but their specific functions are unknown. They accept values 0-100 like other mixer parameters.

**Hypothesis:** These could be additional mixer channels, aux sends, or advanced mixer features not exposed in the standard interface.

# PARAMETER VALUE MAPPINGS

Many parameters have specific value ranges and meanings rather than simple 0-100 ranges:

## MIC/INST Effect Value Ranges

All MIC/INST effect parameters use the standard 0-100 range (hex 00-64) unless otherwise noted:

### MIC/INST Flanger Low Cut (address 10 00 00 1f)
```
00 = FLAT
01 = 55Hz
02 = 110Hz
03 = 165Hz
04 = 200Hz
05 = 280Hz
06 = 340Hz
07 = 400Hz
08 = 500Hz
09 = 530Hz
0A = 800Hz
```

### MIC/INST T.WAH Mode (address 10 00 00 26)
```
00 = LPF (Low Pass Filter)
01 = BPF (Band Pass Filter)
```

### MIC/INST T.WAH Polarity (address 10 00 00 27)
```
00 = UP
01 = DOWN
```

### MIC/INST Equalizer Type (address 10 00 00 00)
```
00 = Type 1
01 = Type 2
02 = Type 3
03 = Type 4
```

### MIC/INST Harmony Key (address 10 00 00 0b)
```
00 = auto
01 = set
```

### MIC/INST Harmony Key Setup (address 10 00 00 0c)
```
00 = C
01 = Db
02 = D
03 = Eb
04 = E
05 = F
06 = Gb
07 = G
08 = Ab
09 = A
0A = Bb
0B = B
```

### MIC/INST Harmony Accurate (address 10 00 00 0d)
```
00 = 1
01 = 2
02 = 3
03 = 4
04 = 5
05 = 6
06 = 7
07 = 8
08 = 9
09 = 10
```

### MIC/INST Harmony Voice Assign (address 10 00 00 0e)
```
00 = default
01 = unison/low/high
02 = unison/low/higher
03 = low/high/higher
```

### MIC/INST Phaser Type (address 10 00 00 19)
```
00 = 4stage
01 = 8stage  
02 = 12stage
03 = BiPHASE
```

### MIC/INST Chorus Xover Frequency (address 10 00 00 18)
```
00 = 200Hz
01 = 250Hz
02 = 315Hz
03 = 400Hz
04 = 500Hz
05 = 630Hz
06 = 800Hz
07 = 1.0kHz
08 = 1.25kHz
09 = 1.6kHz
0A = 2.0kHz
0B = 2.5kHz
0C = 3.15kHz
0D = 4.0kHz
0E = 5.0kHz
0F = 6.3kHz
10 = 8.0kHz
```

## Flanger Low Cut (address 10 00 00 52)
```
00 = FLAT
01 = 55Hz
02 = 110Hz
03 = 165Hz
04 = 200Hz
05 = 280Hz
06 = 340Hz
07 = 400Hz
08 = 500Hz
09 = 530Hz
0A = 800Hz
```

## Reverb Types (address 10 00 00 2d)
```
00 = ROOM
01 = HALL
02 = PLATE
```

## Reverb Knob Assign Functions (address 10 00 00 35)
```
00 = rev time
01 = fx level
```

## Reverb Time (address 10 00 00 2e)
```
Range: 0.1s to 5.0s in 0.1s steps
00 = 0.1s
01 = 0.2s
...
31 = 5.0s (0x31 = 49 decimal)
```

## Reverb Pre-Delay (address 10 00 00 2f, 16-bit)
```
Range: 0ms to 200ms in 1ms steps
00 00 = 0ms
00 01 = 1ms
...
00 C8 = 200ms (0xC8 = 200 decimal)
```

## Delay Time (address 10 00 00 61, 16-bit)
```
Range: 0ms to 1500ms in 1ms steps
00 00 = 0ms
00 01 = 1ms
...
05 DC = 1500ms (0x05DC = 1500 decimal)
```

## T.WAH Mode (address 10 00 00 59 for Guitar, 10 00 00 26 for Mic/Inst)
```
00 = LPF
01 = BPF
```

## T.WAH Polarity (address 10 00 00 5a for Guitar, 10 00 00 27 for Mic/Inst)
```
00 = UP
01 = DOWN
```

## Chorus Pre-Delay (addresses 10 00 00 3d, 10 00 00 42)
```
Range: 0ms to 40ms in 0.5ms steps
00 = 0.0ms
01 = 0.5ms
02 = 1.0ms
...
50 = 25.0ms
...
80 = 40.0ms
```

## Delay Type (address 10 00 00 60)
```
00 = Digital
01 = Reverse
02 = Analog
03 = Tape Echo
```

## Delay Time (address 10 00 00 61, 16-bit)
```