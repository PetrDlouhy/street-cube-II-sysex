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

# MIC/INST T.WAH

```
f0 41 10 00 00 00 00 09 12 10 00 00 26 vv cc f7      # mode (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 27 vv cc f7      # polarity (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 28 vv cc f7      # sens (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 29 vv cc f7      # frequency (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2a vv cc f7      # peak (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2b vv cc f7      # twah level (00 - 64)
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
