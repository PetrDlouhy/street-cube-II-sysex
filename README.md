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


Here are the messages deciphered so far:

# MIXER
```
f0 41 10 00 00 00 00 09 12 20 00 00 00 xx xx xx f7      # mic/instrument (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 01 xx xx xx f7      # guitar/mic (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 02 xx xx xx f7      # i-cube link/aux/bluetooth (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 03 xx xx xx f7      # i-cube link out (00 - 64)
f0 41 10 00 00 00 00 09 12 20 00 00 04 xx xx xx f7      # master out (00 - 64)

f0 41 10 00 00 00 00 09 12 00 00 00 10 xx xx xx f7      # i-cube link loopback (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 17 xx xx xx f7      # USB Audio loopback (00 - 01)
```

# MIC/INST EQUALIZER
```
f0 41 10 00 00 00 00 09 12 10 00 00 00 01 6f a5 f7      # type (00 - 03)
```

# MIC/INST T.WAH

```
f0 41 10 00 00 00 00 09 12 10 00 00 26 00 4a ab f7      # mode (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 27 00 49 cb f7      # polarity (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 28 07 41 a3 f7      # sens (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 29 1a 2d f1 f7      # frequency (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2a 19 2d 97 f7      # peak (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 2b 29 1c a7 f7      # twah level (00 - 64)
```

# MIC/INST REVERB

```
f0 41 10 00 00 00 00 09 12 10 00 00 2d 01 42 b7 f7      # reverb type (00 - 02)
f0 41 10 00 00 00 00 09 12 10 00 00 2e 19 29 86 f7      # reverb time s (00 - 31?)
f0 41 10 00 00 00 00 09 12 10 00 00 2f 00 00 41 ad f7   # pre-delay ms (00 00 - 01 48?)
f0 41 10 00 00 00 00 09 12 10 00 00 31 2d 12 e2 f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 32 09 35 b8 f7      # low cut Hz (00 - 0c)
f0 41 10 00 00 00 00 09 12 10 00 00 33 03 3a c9 f7      # high cut Hz (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 34 06 36 b8 f7      # density (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 35 00 3b fb f7      # knob assign function (00 - 01?)
```

# GUITAR DELAY

```
f0 41 10 00 00 00 00 09 12 10 00 00 60 01 0f e0 f7      # Delay type (00 - 03)
f0 41 10 00 00 00 00 09 12 10 00 00 61 02 7c 11 8f f7   # delay time ms (00 00 - 07 47)

f0 41 10 00 00 00 00 09 12 10 00 00 63 1a 73 83 f7      # feedback (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 64 06 06 e3 f7      # high cut (00 - 0E)

f0 41 10 00 00 00 00 09 12 7f 01 01 03 01 7b e1 f7      # TAP?
f0 41 10 00 00 00 00 09 12 7f 01 01 03 01 7b ab f7

f0 41 10 00 00 00 00 09 12 10 00 00 65 02 09 8f f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 66 01 09 d5 f7      # Knob asign function (00 - 03)
```

# GUITAR AMP TYPE

```
f0 41 10 00 00 00 00 09 12 10 00 00 36 01 39 ad f7      # clean (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 37 01 38 c9 f7      # crunch type (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 38 01 37 fb f7      # lead type (00 - 01)
```

# GUITAR FLANGER
```
f0 41 10 00 00 00 00 09 12 10 00 00 4d 32 71 97 f7      # rate
f0 41 10 00 00 00 00 09 12 10 00 00 4e 20 02 e5 f7      # depth
f0 41 10 00 00 00 00 09 12 10 00 00 4f 2a 77 d3 f7      # resonance
f0 41 10 00 00 00 00 09 12 10 00 00 50 4a 56 c9 f7      # manual
f0 41 10 00 00 00 00 09 12 10 00 00 51 2a 75 f4 f7      # level
f0 41 10 00 00 00 00 09 12 10 00 00 52 02 1c b9 f7      # low cut
```

# GUITAR PHASER
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 01 36 e4 f7      # Switch to phaser
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c f1 f7

f0 41 10 00 00 00 00 09 12 10 00 00 47 5b 4e 89 f7      # rate
f0 41 10 00 00 00 00 09 12 10 00 00 48 20 08 9a f7      # depth
f0 41 10 00 00 00 00 09 12 10 00 00 49 02 25 f3 f7      # resonance

f0 41 10 00 00 00 00 09 12 10 00 00 4a 41 65 f6 f7      # manual
f0 41 10 00 00 00 00 09 12 10 00 00 4b 3a 6b d7 f7      # level

f0 41 10 00 00 00 00 09 12 10 00 00 46 01 29 c7 f7      # type (00 - 03)
```

#  GUITAR CHORUS
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 00 37 8d f7      # Switch to chorus
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c 97 f7

f0 41 10 00 00 00 00 09 12 10 00 00 3b 1b 1a d1 f7      # low rate
f0 41 10 00 00 00 00 09 12 10 00 00 3c 28 0c c3 f7      # low depth
f0 41 10 00 00 00 00 09 12 10 00 00 3d 09 2a b5 f7      # low pre delay
f0 41 10 00 00 00 00 09 12 10 00 00 3e 52 60 96 f7      # low level
f0 41 10 00 00 00 00 09 12 10 00 00 3f 15 1c e1 f7      # direct mix

f0 41 10 00 00 00 00 09 12 10 00 00 40 1b 15 d5 f7      # high rate
f0 41 10 00 00 00 00 09 12 10 00 00 41 06 29 e6 f7      # high depth
f0 41 10 00 00 00 00 09 12 10 00 00 42 0a 24 83 f7      # high pre delay
f0 41 10 00 00 00 00 09 12 10 00 00 43 52 5b e7 f7      # high level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 44 0c 20 eb f7      # xover frequency (00 - 10)
```

# GUITAR TREMOLO
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 03 34 f8 f7      # Switch to tremolo
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c fe f7

f0 41 10 00 00 00 00 09 12 10 00 00 54 3e 5e b5 f7      # wave shape (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 55 4e 4d af f7      # rate (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 56 37 63 ac f7      # depth (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 57 2a 6f e5 f7      # level (00 - 64)
```

# GUITAR T.WAH
```
f0 41 10 00 00 00 00 09 12 10 00 00 39 04 33 c4 f7      # Switch to T.WAH
f0 41 10 00 00 00 00 09 12 7f 01 02 04 7f 7f 7c cd f7

f0 41 10 00 00 00 00 09 12 10 00 00 59 00 17 a6 f7      # Mode (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 5a 00 16 ea f7      # Polarity (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 5b 2a 6b c9 f7      # Sens (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5c 19 7b ba f7      # Frequency (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5d 1a 79 f9 f7      # Peak (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 5e 29 69 ac f7      # Level (00 - 64)
```

# GUIETAR REVERB
```
f0 41 10 00 00 00 00 09 12 10 00 00 2e 19 29 c2 f7      # time (s) (00 - 31)
f0 41 10 00 00 00 00 09 12 10 00 00 2f 00 00 41 92 f7   # pre delay (ms) (00 00 - 01 48)
f0 41 10 00 00 00 00 09 12 10 00 00 67 25 64 8f f7      # effect level (00 - 64)
f0 41 10 00 00 00 00 09 12 10 00 00 32 09 35 9c f7      # low cut (Hz) (00 - 0c)
f0 41 10 00 00 00 00 09 12 10 00 00 33 03 3a b1 f7      # high cut (Hz) (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 34 06 36 a5 f7      # density (00 - 0a)
f0 41 10 00 00 00 00 09 12 10 00 00 35 00 3b 84 f7      # knob assign function (00 - 01)
f0 41 10 00 00 00 00 09 12 10 00 00 2d 01 42 ad f7      # type (00 - 02)
```

# FOOT SWITCH CTRL ASSIGN
```
f0 41 10 00 00 00 00 09 12 00 00 00 04 01 7b fc f7      # sw1-tip (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 05 00 7b ab f7      # sw1-ring (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 06 00 7a b5 f7      # sw2-tip (00 - 05)
f0 41 10 00 00 00 00 09 12 00 00 00 07 00 79 c0 f7      # sw2-ring (00 - 05)
```

# LOOPER SETTINGS
```
f0 41 10 00 00 00 00 09 12 00 00 00 0a 01 75 d4 f7      # Rec time (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0b 01 74 b4 f7      # mic/instrument assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0c 01 73 e8 f7      # guitar/mic assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0d 01 72 d1 f7      # reverb assign (00 - 01)
f0 41 10 00 00 00 00 09 12 00 00 00 0e 01 71 8b f7      # i-cube link/aux/bluetooth assign (00 - 01)
```
