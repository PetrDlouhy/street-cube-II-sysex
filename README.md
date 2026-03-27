# Boss CUBE Street II — SysEx Reference

Complete SysEx parameter map for the Boss CUBE Street II amplifier.
Based on Roland's official `address_map.js` extracted from the
[CUBE Street II Editor](https://play.google.com/store/apps/details?id=jp.co.roland.boss_cube_street_II_editor)
Android app, supplemented by live BLE traffic analysis.

## Contents

- [SysEx Message Format](#sysex-message-format)
- **Parameter Reference**
  - [System Setup (00 00 00 xx)](#system-setup-00-00-00-xx)
  - [Mic/Inst Effects (10 00 00 00–2B)](#micinst-effects-10-00-00-00–2b)
  - [Reverb (10 00 00 2C–35)](#reverb-10-00-00-2c–35)
  - [Guitar Effects (10 00 00 36–6C)](#guitar-effects-10-00-00-36–6c)
  - [Mixer (20 00 00 xx)](#mixer-20-00-00-xx)
  - [Panel Controls (20 00 20 xx)](#panel-controls-20-00-20-xx)
  - [Status & Looper (20 00 10 xx)](#status--looper-20-00-10-xx)
  - [Tuner Config (20 00 30 xx)](#tuner-config-20-00-30-xx)
  - [System Commands (7F xx xx xx)](#system-commands-7f-xx-xx-xx)
- [Tuner Data Format](#tuner-data-format)
- [Usage Guide](#usage-guide)
- [Technical Notes](#technical-notes)
- [Reverse Engineering](#reverse-engineering)
  - [Extracting the Address Map from the Editor App](#method-1-extracting-the-official-address-map-from-the-editor-app)
  - [BLE Traffic Capture (HCI Snoop)](#method-2-ble-traffic-capture-hci-snoop)
  - [Live Discovery via Web App](#method-3-live-discovery-via-web-app)
- [Web App](#web-app)

---

## SysEx Message Format

```
F0 41 10 00 00 00 00 09 <cmd> <addr ×4> <data...> <checksum> F7
```

| Field | Bytes | Description |
|-------|-------|-------------|
| `F0` | 1 | SysEx start |
| `41` | 1 | Roland manufacturer ID |
| `10` | 1 | Device ID (broadcast) |
| `00 00 00 00 09` | 5 | Model ID (CUBE Street II) |
| cmd | 1 | `11` = Read request (RQ1), `12` = Data set (DT1) |
| addr | 4 | Parameter address |
| data | 1+ | Value (DT1) or read size (RQ1) |
| checksum | 1 | Roland checksum |
| `F7` | 1 | SysEx end |

**Roland checksum:** `(128 - (sum(addr + data) % 128)) % 128`

The amp does not verify the checksum — any value is accepted.

**BLE MIDI framing (important):** The Boss Cube uses BLE MIDI, not classic
MIDI. Most standard MIDI/SysEx sender apps fail to control the Cube because
BLE MIDI wraps SysEx messages in a specific framing with timestamp bytes:

```
<BLE header> <timestamp> F0 <sysex data...> <timestamp> F7
```

Without the timestamp byte before `F7`, the amp silently ignores the message.
Apps that send raw SysEx bytes over Bluetooth will appear to work (no error)
but the amp never receives the data. MIDI Commander is one app that handles
BLE MIDI SysEx correctly. The Web Bluetooth API (used by the web app) also
handles this transparently.

---

## Parameter Reference

Ranges and init (factory default) values are decimal unless noted with `0x`.
Parameters marked *2×7* use [Roland 7-bit encoding](#roland-7-bit-encoding).
Parameters marked *read-only* are sent by the amp but reject writes.

### System Setup (00 00 00 xx)

Persistent settings — survive power cycles.
Roland block: `prm_prop_setup_sys`.

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 00 00 00 00 | USB Mix Level | 0–100 | 50 | *2×7*. 0%–200%, 2% steps. 50 = 100% |
| 00 00 00 02 | USB Master Out Level | 0–100 | 50 | *2×7*. Same scale as above |
| 00 00 00 04 | Foot SW1 Tip | 0–5 | 1 | Off, Guitar FX, Mic/Inst FX, Delay, Reverb, Looper |
| 00 00 00 05 | Foot SW1 Ring | 0–5 | 2 | (same) |
| 00 00 00 06 | Foot SW2 Tip | 0–5 | 3 | (same) |
| 00 00 00 07 | Foot SW2 Ring | 0–5 | 4 | (same) |
| 00 00 00 08 | Stereo Link Mode | 0–2 | 0 | Off, Host, Remote |
| 00 00 00 09 | Stereo Input Mode | 0–1 | 0 | Off, On |
| 00 00 00 0A | Looper Rec Time | 0–1 | 0 | 45s Stereo, 90s Mono |
| 00 00 00 0B | Looper Mic/Inst Assign | 0–1 | 1 | Off, On |
| 00 00 00 0C | Looper Guitar/Mic Assign | 0–1 | 1 | Off, On |
| 00 00 00 0D | Looper Reverb Assign | 0–1 | 1 | Off, On |
| 00 00 00 0E | Looper i-CUBE/AUX/BT Assign | 0–1 | 1 | Off, On |
| 00 00 00 0F | Mix Level Reserved | 0–100 | 50 | Roland marks "reserved" — purpose unclear |
| 00 00 00 10 | i-CUBE LINK Loopback | 0–1 | 0 | Off, On |
| 00 00 00 11 | AUX IN Ducking | 0–1 | 0 | Off, On |
| 00 00 00 12 | AUX IN Ducking Level | 0–100 | 10 | |
| 00 00 00 13 | Noise Suppressor Mic/Inst | 0–1 | 1 | Off, On |
| 00 00 00 14 | Noise Suppressor Guitar/Mic | 0–1 | 1 | Off, On |
| 00 00 00 15 | Noise Suppressor i-CUBE/AUX/BT | 0–1 | 1 | Off, On |
| 00 00 00 16 | Bluetooth ID | 0–2 | 0 | Suffix on BLE name. 0 = no suffix |
| 00 00 00 17 | USB Audio Loopback | 0–1 | 1 | Off, On |
| 00 00 00 18 | Apply Panel Condition | 0–1 | 1 | Apply physical knob positions on startup |
| 00 00 00 19 | Harmony Key Mode | 0–1 | 0 | Auto (green LED), Set (red LED) |
| 00 00 00 1A | Harmony Key Setup | 0–16 | 0 | C, C♯, D♭, D, D♯, E♭, E, F, F♯, G♭, G, G♯, A♭, A, A♯, B♭, B |

> **Note:** USB levels at addresses 00–03 do not respond to individual RQ1
> reads. They are only accessible via [block read](#block-reads) of the full
> system range. Harmony Key addresses 19–1A are the **system-level** copies
> that receive hardware button feedback. See also the
> [effect-level mirrors](#shared-and-mirrored-addresses) at 10 00 00 04–05.

### Mic/Inst Effects (10 00 00 00–2B)

Roland block: `prm_prop_sys` (PATCH), base address `10 00 00 00`.

#### EQ & Effect Selector

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 00 | EQ Type | 0–3 | 0 | Off, Speech, Vocal, Inst |
| 10 00 00 01 | Effect Type | 0–5 | 0 | Harmony, Chorus, Phaser, Flanger, Tremolo, T.WAH |

#### Harmony

On/off pattern differs from other effects — uses dedicated address 02.

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 02 | On/Off | 0–1 | 0 | |
| 10 00 00 03 | Voice Assign | 0–3 | 0 | Default, Unison/Low/High, Unison/Low/Higher, Low/High/Higher |
| 10 00 00 04 | Key Mode *(mirror)* | 0–1 | 0 | Mirror of 00 00 00 19. No HW feedback |
| 10 00 00 05 | Key Setup *(mirror)* | 0–16 | 0 | Mirror of 00 00 00 1A. No HW feedback |
| 10 00 00 06 | Accurate | 0–9 | 9 | Display as 1–10 |
| 10 00 00 6A | Harmony Type | 0–5 | 5 | Active voice zone — changes at knob detents |
| 10 00 00 6B | Harmony Level | 0–100 | 0 | Mirrors [HARMONY] knob position |

Addresses 0B–0E are [shared with Chorus](#shared-and-mirrored-addresses).
When Harmony is active, they hold: Key (0B), Key Setup (0C), Accurate (0D),
Voice Assign (0E). Dedicated copies at 03 and 06 above are always accessible.

#### Chorus

On/off at first address minus one. Addresses 0B–0E shared with Harmony config.

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 07 | On/Off | 0–1 | 0 | |
| 10 00 00 08 | Low Rate | 0–100 | 39 | |
| 10 00 00 09 | Low Depth | 0–100 | 50 | |
| 10 00 00 0A | Low Pre Delay | 0–80 | 16 | |
| 10 00 00 0B | Low Level | 0–100 | 90 | *Shared with Harmony Key* |
| 10 00 00 0C | Direct Mix | 0–100 | 30 | *Shared with Harmony Key Setup* |
| 10 00 00 0D | High Rate | 0–100 | 30 | *Shared with Harmony Accurate* |
| 10 00 00 0E | High Depth | 0–100 | 0 | *Shared with Harmony Voice Assign* |
| 10 00 00 0F | High Pre Delay | 0–80 | 16 | |
| 10 00 00 10 | High Level | 0–100 | 90 | |
| 10 00 00 11 | Xover Freq | 0–16 | 14 | 200 Hz … 8.0 kHz (17 steps) |

<details><summary>Xover Frequency values</summary>

0=200, 1=250, 2=315, 3=400, 4=500, 5=630, 6=800, 7=1.0k, 8=1.25k,
9=1.6k, 10=2.0k, 11=2.5k, 12=3.15k, 13=4.0k, 14=5.0k, 15=6.3k, 16=8.0k Hz

</details>

#### Phaser

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 12 | On/Off | 0–1 | 0 | |
| 10 00 00 13 | Type | 0–3 | 0 | 4-Stage, 8-Stage, 12-Stage, BiPhase |
| 10 00 00 14 | Rate | 0–100 | 70 | |
| 10 00 00 15 | Depth | 0–100 | 40 | |
| 10 00 00 16 | Resonance | 0–100 | 0 | |
| 10 00 00 17 | Manual | 0–100 | 55 | |
| 10 00 00 18 | Level | 0–100 | 50 | |

#### Flanger

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 19 | On/Off | 0–1 | 0 | |
| 10 00 00 1A | Rate | 0–100 | 31 | |
| 10 00 00 1B | Depth | 0–100 | 40 | |
| 10 00 00 1C | Resonance | 0–110 | 50 | Note: max 110, not 100 |
| 10 00 00 1D | Manual | 0–100 | 82 | |
| 10 00 00 1E | Level | 0–100 | 50 | |
| 10 00 00 1F | Low Cut | 0–10 | 0 | Flat, 55, 110, 165, 200, 280, 340, 400, 500, 530, 800 Hz |

#### Tremolo

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 20 | On/Off | 0–1 | 0 | |
| 10 00 00 21 | Wave Shape | 0–100 | 70 | |
| 10 00 00 22 | Rate | 0–100 | 85 | |
| 10 00 00 23 | Depth | 0–100 | 65 | |
| 10 00 00 24 | Level | 0–100 | 50 | |

#### T.WAH

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 25 | On/Off | 0–1 | 0 | |
| 10 00 00 26 | Mode | 0–1 | 1 | LPF, BPF |
| 10 00 00 27 | Polarity | 0–1 | 1 | Down, Up |
| 10 00 00 28 | Sens | 0–100 | 50 | |
| 10 00 00 29 | Frequency | 0–100 | 35 | |
| 10 00 00 2A | Peak | 0–100 | 35 | |
| 10 00 00 2B | Level | 0–100 | 50 | |

### Reverb (10 00 00 2C–35)

Shared reverb unit — type, time, and settings apply to both channels.
Per-channel effect levels at 31 (Mic/Inst) and 67 (Guitar).

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 2C | On/Off | 0–1 | 0 | |
| 10 00 00 2D | Type | 0–2 | 2 | Room, Hall, Plate |
| 10 00 00 2E | Time | 0–49 | 29 | 0.1 s – 5.0 s |
| 10 00 00 2F | Pre-Delay | 0–200 | 10 | *2×7*. 0–200 ms |
| 10 00 00 31 | Mic/Inst Effect Level | 0–100 | 50 | |
| 10 00 00 32 | Low Cut | 0–12 | 10 | Flat, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630 Hz |
| 10 00 00 33 | High Cut | 0–10 | 4 | 1.6k, 2.0k, 2.5k, 3.15k, 4.0k, 5.0k, 6.3k, 8.0k, 10.0k, 12.5k Hz, Flat |
| 10 00 00 34 | Density | 0–10 | 7 | |
| 10 00 00 35 | Knob Assign | 0–1 | 1 | Rev Time, FX Level |

### Guitar Effects (10 00 00 36–6C)

#### Amp Types

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 36 | Clean Amp Type | 0–1 | 0 | Type-A, Type-B |
| 10 00 00 37 | Crunch Amp Type | 0–1 | 0 | Type-A, Type-B |
| 10 00 00 38 | Lead Amp Type | 0–1 | 0 | Type-A, Type-B |

#### Effect Selector

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 39 | Effect Type | 0–4 | 0 | Chorus, Phaser, Flanger, Tremolo, T.WAH |
| 10 00 00 6C | Chorus/Delay Selector | 0–2 | 0 | Selects what [CHORUS/DELAY] knob controls |

#### Chorus

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 3A | On/Off | 0–1 | 0 | |
| 10 00 00 3B | Low Rate | 0–100 | 39 | |
| 10 00 00 3C | Low Depth | 0–100 | 50 | |
| 10 00 00 3D | Low Pre Delay | 0–80 | 16 | |
| 10 00 00 3E | Low Level | 0–100 | 90 | |
| 10 00 00 3F | Direct Mix | 0–100 | 30 | |
| 10 00 00 40 | High Rate | 0–100 | 30 | |
| 10 00 00 41 | High Depth | 0–100 | 0 | |
| 10 00 00 42 | High Pre Delay | 0–80 | 16 | |
| 10 00 00 43 | High Level | 0–100 | 90 | |
| 10 00 00 44 | Xover Freq | 0–16 | 14 | Same scale as [Mic/Inst Chorus](#chorus) |

#### Phaser

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 45 | On/Off | 0–1 | 0 | |
| 10 00 00 46 | Type | 0–3 | 0 | 4-Stage, 8-Stage, 12-Stage, BiPhase |
| 10 00 00 47 | Rate | 0–100 | 70 | |
| 10 00 00 48 | Depth | 0–100 | 40 | |
| 10 00 00 49 | Resonance | 0–100 | 0 | |
| 10 00 00 4A | Manual | 0–100 | 55 | |
| 10 00 00 4B | Level | 0–100 | 50 | |

#### Flanger

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 4C | On/Off | 0–1 | 0 | |
| 10 00 00 4D | Rate | 0–100 | 31 | |
| 10 00 00 4E | Depth | 0–100 | 40 | |
| 10 00 00 4F | Resonance | 0–100 | 50 | |
| 10 00 00 50 | Manual | 0–100 | 82 | |
| 10 00 00 51 | Level | 0–100 | 50 | |
| 10 00 00 52 | Low Cut | 0–10 | 0 | Same scale as [Mic/Inst Flanger](#flanger) |

#### Tremolo

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 53 | On/Off | 0–1 | 0 | |
| 10 00 00 54 | Wave Shape | 0–100 | 70 | |
| 10 00 00 55 | Rate | 0–100 | 85 | |
| 10 00 00 56 | Depth | 0–100 | 65 | |
| 10 00 00 57 | Level | 0–100 | 50 | |

#### T.WAH

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 58 | On/Off | 0–1 | 0 | |
| 10 00 00 59 | Mode | 0–1 | 1 | LPF, BPF |
| 10 00 00 5A | Polarity | 0–1 | 1 | Down, Up |
| 10 00 00 5B | Sens | 0–100 | 50 | |
| 10 00 00 5C | Frequency | 0–100 | 35 | |
| 10 00 00 5D | Peak | 0–100 | 35 | |
| 10 00 00 5E | Level | 0–100 | 50 | |

#### Delay

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 5F | On/Off | 0–1 | 0 | |
| 10 00 00 60 | Type | 0–3 | 0 | Digital, Reverse, Analog, Tape Echo |
| 10 00 00 61 | Time | 0–999 | 434 | *2×7*. 0–999 ms |
| 10 00 00 63 | Feedback | 0–100 | 35 | |
| 10 00 00 64 | High Cut | 0–14 | 8 | 630, 800 Hz, 1.0k, 1.25k, 1.6k, 2.0k, 2.5k, 3.15k, 4.0k, 5.0k, 6.3k, 8.0k, 10.0k, 12.5k Hz, Flat |
| 10 00 00 65 | Effect Level | 0–120 | 0 | Note: max 120, not 100 |
| 10 00 00 66 | Knob Assign | 0–3 | 0 | Default, Delay Time, Feedback, FX Level |

#### Additional Guitar Parameters

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 10 00 00 67 | Guitar Reverb Level | 0–100 | 50 | |
| 10 00 00 68 | Tuner Reference Pitch | 0–10 | 5 | 435–445 Hz (5 = 440 Hz) |
| 10 00 00 69 | Guitar Reverb On/Off | 0–1 | 0 | |

### Mixer (20 00 00 xx)

Roland block: `prm_prop_temp_sys`. These persist across power cycles.

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 20 00 00 00 | Mic/Inst Volume | 0–100 | 50 | |
| 20 00 00 01 | Guitar/Mic Volume | 0–100 | 50 | |
| 20 00 00 02 | i-CUBE LINK/AUX/BT Volume | 0–100 | 50 | |
| 20 00 00 03 | i-CUBE LINK Out Volume | 0–100 | 50 | |
| 20 00 00 04 | Master Out Volume | 0–100 | 50 | |

### Panel Controls (20 00 20 xx)

Physical knob/switch positions. **Read-only** — the amp sends these when
controls are moved but rejects writes. Not in Roland's `address_map.js`.

| Address | Parameter | Range | Values |
|---------|-----------|------:|--------|
| 20 00 20 00 | Phones/Rec Out Jack | 0–1 | Unplugged, Inserted |
| 20 00 20 01 | Mic/Inst EQ Bass | 0–100 | |
| 20 00 20 02 | Mic/Inst EQ Middle | 0–100 | |
| 20 00 20 03 | Mic/Inst EQ Treble | 0–100 | |
| 20 00 20 04 | Guitar EQ Bass | 0–100 | |
| 20 00 20 05 | Guitar EQ Middle | 0–100 | |
| 20 00 20 06 | Guitar EQ Treble | 0–100 | |
| 20 00 20 07 | Guitar Gain | 0–100 | |
| 20 00 20 08 | Guitar/Mic Volume Knob | 0–100 | |
| 20 00 20 09 | Mic/Inst Input Select | 0–1 | Mic, Inst |
| 20 00 20 0A | Guitar Amp Type | 0–8 | Acoustic, Normal, Bright, Wide, Inst, Clean, Crunch, Lead, Mic |
| 20 00 20 0B | AUX IN Volume Knob | 0–100 | |
| 20 00 20 0C | Audio Output Mute | 0–1 | Muted, On |
| 20 00 20 0D | Output Power Mode | 0–1 | Eco, Max |
| 20 00 20 0E | [HARMONY] Knob | 0–100 | Mic/Inst effect level |
| 20 00 20 0F | [REVERB] Knob (Mic/Inst) | 0–100 | |
| 20 00 20 10 | [REVERB] Knob (Guitar) | 0–100 | |
| 20 00 20 11 | [CHORUS/DELAY] Knob | 0–100 | Guitar effect/delay level |
| 20 00 20 12 | Unknown | 0–5 | Purpose unknown. Factory default 5 |

### Status & Looper (20 00 10 xx)

| Address | Parameter | Range | Values |
|---------|-----------|------:|--------|
| 20 00 10 00 | Tuner On/Off | 0–1 | Off, On |
| 20 00 10 01 | Looper Control | 0–5 | Erase, Paused, Recording, Playing, Overdub, Standby |
| 20 00 10 02 | Battery Low | 0–1 | OK, Low (power LED flashes) |

### Tuner Config (20 00 30 xx)

Roland block: `prm_prop_temp_tuner`. Activated by long-pressing the tuner button.

| Address | Parameter | Range | Init | Values |
|---------|-----------|------:|-----:|--------|
| 20 00 30 00 | Tuner Mode | 0–1 | 0 | Chromatic, Manual |
| 20 00 30 01 | Manual Note | 0–8 | 2 | C, D, E, F, G, A, B, 5A, 5A♭ |
| 20 00 30 02 | Accidental | 0–2 | 1 | Flat, Natural, Sharp |

### System Commands (7F xx xx xx)

Not in Roland's `address_map.js` — discovered by BLE capture.

| Address | Parameter | Values |
|---------|-----------|--------|
| 7F 00 00 01 | Notification Control | 0 = disable, 1 = enable continuous notifications |
| 7F 00 00 02 | Tuner Streaming | 0 = stopped, 1 = streaming pitch data |
| 7F 00 03 00 | Tuner Data | 6-byte pitch data (read-only, see [Tuner Data Format](#tuner-data-format)) |
| 7F 00 05 02 | Battery Level | 1 = 1 bar (low), 3 = 3 bars (full) |
| 7F 01 01 03 | Delay TAP Tempo | Sent on each tap |
| 7F 01 02 04 | Effect Activate | Always followed by `7F 7F`. Apply pending changes |

---

## Tuner Data Format

When the tuner is enabled (`7F 00 00 02` = 1), the amp continuously streams
6-byte pitch data at `7F 00 03 00`.

**Decoding:**

```
Byte 0: base frequency / note
Byte 1: cents deviation high (0–2)
Byte 2: cents deviation low (0–15)
Byte 3–5: fine-tuning / unknown
```

```
rawTunerValue   = (byte1 << 4) | byte2       // 6-bit, 0–63
centsDeviation  = (rawTunerValue - 19) * 3   // center = 19 → 0¢

baseFreq        = 220.0                       // A3
freqMultiplier  = 2 ^ ((byte0 - 57) / 12)
frequency       = baseFreq * freqMultiplier + (byte3 * 0.1)

noteNumber      = round(12 * log2(frequency / 440) + 69)
noteName        = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][noteNumber % 12]
octave          = floor(noteNumber / 12) - 1
```

"In Tune" when |centsDeviation| ≤ 3¢ (matches the hardware green LED range).

**Examples:**
| Data | Decoded |
|------|---------|
| `40 01 03 00 00 00` | E4 329.6 Hz, 0¢ (in tune) |
| `40 01 02 00 00 00` | E4 329.4 Hz, −3¢ (in tune) |
| `40 01 01 00 00 00` | E4 329.1 Hz, −6¢ (flat) |
| `00 00 00 00 00 00` | No signal |

---

## Usage Guide

### MIDI Commander

Works with [MIDI Commander](https://www.bordero.it/Apps/MidiCommander/)
by entering the middle portion (the app adds `F0` and `F7` automatically):

```
41 10 00 00 00 00 09 12 20 00 00 04 %V
```

### Reading a Parameter

Send a **RQ1** (command `11`) with the read size instead of a value:

```
→ F0 41 10 00 00 00 00 09 11 20 00 00 04 00 00 00 01 5B F7   # Read master volume
← F0 41 10 00 00 00 00 09 12 20 00 00 04 32 2C F7             # Response: 50 (0x32)
```

The 4-byte field after the address is the read **size**, not a value.
The amp responds with a DT1 (command `12`) containing the current value.

### Writing a Parameter

```
F0 41 10 00 00 00 00 09 12 20 00 00 04 32 2C F7   # Set master volume to 50
F0 41 10 00 00 00 00 09 12 10 00 00 01 02 7D F7   # Switch Mic/Inst to Phaser
```

### Looper Control

```
F0 41 10 00 00 00 00 09 12 20 00 10 01 05 4A F7   # Standby
F0 41 10 00 00 00 00 09 12 20 00 10 01 02 4D F7   # Start recording
F0 41 10 00 00 00 00 09 12 20 00 10 01 03 4C F7   # Playing
F0 41 10 00 00 00 00 09 12 20 00 10 01 04 4B F7   # Overdub
F0 41 10 00 00 00 00 09 12 20 00 10 01 00 4F F7   # Erase
```

### Initialization Sequence

Enable continuous notifications first, then read all parameter blocks:

```
→ F0 41 10 00 00 00 00 09 12 7F 00 00 01 01 7F F7             # Enable notifications
→ F0 41 10 00 00 00 00 09 11 00 00 00 00 00 00 00 1B 65 F7   # Read system block (27 bytes)
→ F0 41 10 00 00 00 00 09 11 10 00 00 00 00 00 00 6D 03 F7   # Read effects block (109 bytes)
→ F0 41 10 00 00 00 00 09 11 20 00 00 00 00 00 00 05 5B F7   # Read mixer block (5 bytes)
→ F0 41 10 00 00 00 00 09 11 20 00 20 00 00 00 00 13 2D F7   # Read panel block (19 bytes)
→ F0 41 10 00 00 00 00 09 11 20 00 10 00 00 00 00 03 4D F7   # Read status block (3 bytes)
→ F0 41 10 00 00 00 00 09 11 20 00 30 00 00 00 00 03 2D F7   # Read tuner config (3 bytes)
```

Add 100–150 ms delays between requests to avoid overwhelming the device.

### Physical Knob vs Read Response

The amp uses the same DT1 format for both read responses and unsolicited
knob-change notifications. To distinguish: if a response arrives within
~2 seconds of a RQ1 to the same address, it's a read response. Otherwise,
it's a physical control change.

---

## Technical Notes

### Shared and Mirrored Addresses

**Shared effect addresses (0B–0E):** When Harmony is the active Mic/Inst
effect, addresses 10 00 00 0B–0E hold Harmony config (Key, Key Setup,
Accurate, Voice Assign). When Chorus is active, the same addresses hold
Chorus params (Low Level, Direct Mix, High Rate, High Depth). Dedicated
copies at 03 (Voice Assign) and 06 (Accurate) are always accessible
regardless of which effect is active.

**System vs effect mirrors:** Harmony Key Mode and Key Setup exist at two
address levels:
- **System** (00 00 00 19–1A): receives hardware button feedback
- **Effect** (10 00 00 04–05): written by the app but does not receive
  hardware feedback

Use the system addresses for UI controls that need to reflect physical
button presses.

### Roland 7-bit Encoding

Parameters marked *2×7* (`INTEGER2x7`) occupy 2 SysEx bytes:

```
actual_value = (byte0 << 7) | byte1
```

Example: Delay Time 434 ms → bytes `03 37` (3×128 + 55 = 439). The second
byte's address does not respond to individual reads — use block reads.

### Block Reads

A single RQ1 can read a contiguous address range. The `size` field specifies
how many bytes to read. The amp responds with one DT1 containing all values.

Some addresses (USB levels at 00 00 00 00–03) **only** respond to block
reads and silently ignore individual RQ1 requests. The official app always
reads these as blocks.

### Effect On/Off Pattern

For most effects: `on_off_address = first_param_address - 1`.
Harmony is the exception — its on/off is at 0x02.
Reverb on/off at 0x2C follows the pattern (before first param at 0x2D).

---

## Reverse Engineering

These methods are applicable to other Roland/Boss devices with minor
adjustments (different package names, model IDs, and address ranges).

### Method 1: Extracting the Official Address Map from the Editor App

This is the single most valuable step. Roland's editor apps (Boss Tone
Studio, CUBE Street II Editor, etc.) are web-based apps (HTML/JS/CSS)
packaged inside Android/iOS containers. The complete SysEx address map is
embedded as **plain JavaScript** — no decompilation needed.

#### Android APK extraction

```bash
# 1. Connect phone via USB with USB debugging enabled
adb devices                    # phone will prompt to authorize

# 2. Find the APK path
adb shell pm path jp.co.roland.boss_cube_street_II_editor
# returns: package:/data/app/.../base.apk

# 3. Pull and extract
adb pull /data/app/.../base.apk base.apk
unzip base.apk -d extracted
```

The address map is at `extracted/assets/html/js/config/address_map.js`.

Each parameter entry has: SysEx address, byte size (`INTEGER1x7` = 1 byte,
`INTEGER2x7` = 2 bytes 7-bit encoded), min/max range, init (default) value,
and official Roland parameter name.

Other useful files in the APK:

| File | Contents |
|------|----------|
| `js/config/editor_setting.js` | UI layout, display names, value labels |
| `js/config/product_setting.js` | Device capabilities and feature flags |
| `js/common/parameter.js` | Parameter encoding/decoding logic |

#### Other Roland/Boss devices

Other Roland editor apps (e.g., Boss Tone Studio for Katana) use the same
web-based architecture. The `address_map.js` file should be extractable
the same way. Desktop editors may also have the web assets unpacked on disk
in their installation directory.

#### Note on firmware

The `.BIN` firmware update files are AES-encrypted. Don't waste time trying
to disassemble them — the APK approach yields far more useful data.

### Method 2: BLE Traffic Capture (HCI Snoop)

Captures actual BLE MIDI traffic between the official app and the device.
Useful for understanding initialization sequences, block read patterns, and
verifying parameter behavior.

#### Capture procedure (Android)

1. **Settings → Developer Options → Enable "Bluetooth HCI snoop log"**
2. Toggle Bluetooth off/on to start a fresh capture
3. Use the official app — perform the actions you want to observe
4. Toggle Bluetooth off/on again to flush the log to disk
5. Pull the log:

```bash
adb pull /data/misc/bluetooth/logs/btsnoop_hci.log
```

The log path varies by Android version and manufacturer. On Samsung, it may
be in a different location — use a file manager app or try:

```bash
adb shell find /data -name "btsnoop*" 2>/dev/null
```

#### Analysis

Quick inspection with tshark:

```bash
tshark -r btsnoop_hci.log -Y "btatt.value" -T fields \
  -e frame.time_relative -e btatt.opcode -e btatt.value
```

This repo includes `parse_btsnoop.py` which automates the full pipeline:
extracts ATT values, strips BLE MIDI timestamps, reassembles fragmented
SysEx messages, and parses Roland-format messages with named parameter
lookup.

```bash
python3 parse_btsnoop.py path/to/btsnoop_hci.log
```

Key discovery from HCI analysis: some addresses (e.g., USB Mix/Master levels
at `00 00 00 00–03`) only respond to **block reads**, not individual RQ1
requests. The official app always reads these as contiguous blocks.

### Method 3: Live Discovery via Web App

The [Boss Cube Web Control](#web-app) app includes a built-in SysEx
Discovery Dashboard (gear menu) with:

- **Live Monitor** — records all incoming SysEx in real-time
- **Range Scanner** — block reads of known address ranges with diff
  comparison between scans
- **Tweak Unknowns** — directly read/write unknown addresses with a custom
  address probe for exploring the address space

---

## Web App

**[Boss Cube Web Control](../boss-cube-web-control/)** — an open-source
Progressive Web App implementing complete wireless control over the Boss
CUBE Street II via Web Bluetooth. Features include a full mixer interface,
all effects controls, EV-1-WL expression pedal support, live performance
mode, and a built-in SysEx discovery dashboard.
