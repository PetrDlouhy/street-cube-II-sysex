#!/usr/bin/env python3
"""
This script controls a Boss Cube II amplifier using a BLE MIDI pedal (EV-1-WL).

It allows for multi-parameter control, including volume, reverb, and various effects.

It uses gatttool for BLE communication and mido for MIDI handling, altough the end goal is to use some simpler, more relieable way like `mido`, but `mido` doesn't send the correct handlery yet.
"""
import mido
import subprocess
import time
import sys
import threading
from typing import Optional, List

DEVICE_ADDRESS = "fb:b7:d0:2d:4a:2d"
BOSS_CUBE_HEADER = [0x41, 0x10, 0x00, 0x00, 0x00, 0x00, 0x09, 0x12]

class Parameter:
    """Boss Cube parameter definition"""
    def __init__(self, name: str, address: List[int], min_val: int, max_val: int, 
                 effect_switch_commands: List[List[int]] = None):
        self.name = name
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
        self.effect_switch_commands = effect_switch_commands or []
        self.current_value = min_val

# Define controllable parameters
PARAMETERS = [
    Parameter("Master Volume", [0x20, 0x00, 0x00, 0x04], 0, 100),
    Parameter("Guitar Reverb Time", [0x10, 0x00, 0x00, 0x2e], 0, 49),  # 0-31 seconds according to README
    Parameter("Guitar Reverb Level", [0x10, 0x00, 0x00, 0x67], 0, 100),
    Parameter("Guitar Phaser Level", [0x10, 0x00, 0x00, 0x4b], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x01],  # Switch to phaser
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f]  # Standard effect activation
    ]),
    Parameter("Guitar Chorus Level", [0x10, 0x00, 0x00, 0x43], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x00],  # Switch to chorus
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f]  # Standard effect activation
    ]),
    Parameter("Guitar Tremolo Level", [0x10, 0x00, 0x00, 0x57], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x03],  # Switch to tremolo
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f]  # Standard effect activation
    ]),
    Parameter("Guitar T.WAH Level", [0x10, 0x00, 0x00, 0x5e], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x04],  # Switch to T.WAH
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f]  # Standard effect activation
    ]),
]

def roland_checksum(data_bytes):
    """Calculate Roland checksum"""
    total = sum(data_bytes)
    remainder = total % 128
    checksum = (128 - remainder) % 128
    return checksum

def create_ble_midi_command(sysex_data):
    """Create BLE MIDI command from SysEx data"""
    ble_midi_header = "8080"
    timestamp = "f0"
    sysex_body = "".join(f"{b:02x}" for b in sysex_data)
    sysex_end = "f7"
    
    return ble_midi_header + timestamp + sysex_body + timestamp + sysex_end

class BLEMIDIHandler:
    """Simple BLE MIDI handler using gatttool"""
    
    def __init__(self, device_address: str):
        self.device_address = device_address
        self.characteristic_handle = "0x000c"
        self.process = None
        self.is_connected = False
        self.output_buffer = []
        self.output_thread = None
    
    def _read_output(self):
        """Read gatttool output in a separate thread"""
        if not self.process:
            return
        
        while self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_buffer.append(line.strip())
                    print(f"gatttool: {line.strip()}")
            except:
                break
    
    def connect(self) -> bool:
        """Connect to device using gatttool"""
        try:
            print(f"Connecting to {self.device_address}...")
            
            self.process = subprocess.Popen(
                ["gatttool", "-b", self.device_address, "-I"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Start output reading thread
            self.output_thread = threading.Thread(target=self._read_output)
            self.output_thread.daemon = True
            self.output_thread.start()
            
            # Send connect command
            self.process.stdin.write("connect\n")
            self.process.stdin.flush()
            
            # Wait for connection and check output
            connection_timeout = 10
            start_time = time.time()
            
            while (time.time() - start_time) < connection_timeout:
                if self.process.poll() is not None:
                    print("gatttool process terminated")
                    return False
                
                # Check for connection success in output
                for line in self.output_buffer:
                    if "Connection successful" in line:
                        self.is_connected = True
                        print("BLE connection established")
                        return True
                    elif "Connection failed" in line or "Can't connect" in line:
                        print("Connection failed")
                        return False
                
                time.sleep(0.1)
            
            print("Connection timeout")
            return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            self.cleanup()
            
        return False
    
    def send_command(self, command_hex: str) -> bool:
        """Send BLE MIDI command (fast but reliable)"""
        if not self.is_connected or not self.process:
            return False
        
        try:
            cmd = f"char-write-req {self.characteristic_handle} {command_hex}\n"
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
            
            # Very short wait for acknowledgment (balance speed vs reliability)
            time.sleep(0.1)
            return True
            
        except Exception as e:
            print(f"Send command error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.process and self.is_connected:
            try:
                self.process.stdin.write("disconnect\n")
                self.process.stdin.write("exit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=5)
            except:
                pass
            finally:
                self.cleanup()
    
    def cleanup(self):
        """Clean up process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            finally:
                self.process = None
                self.is_connected = False

def send_parameter_command(ble_handler, parameter: Parameter, value: int):
    """Send parameter control command to Boss Cube (value only)"""
    # Clamp value to parameter range
    value = max(parameter.min_val, min(parameter.max_val, value))
    parameter.current_value = value
    
    # Send parameter value command only (no effect switching)
    data = [value]
    syx = BOSS_CUBE_HEADER + parameter.address + data + [roland_checksum(parameter.address + data)]
    command = create_ble_midi_command(syx)
    
    return ble_handler.send_command(command)

def send_effect_switch_commands(ble_handler, parameter: Parameter):
    """Send effect switch commands for a parameter"""
    for switch_cmd in parameter.effect_switch_commands:
        # Add checksum to switch command
        switch_syx = BOSS_CUBE_HEADER + switch_cmd + [roland_checksum(switch_cmd)]
        switch_command = create_ble_midi_command(switch_syx)
        ble_handler.send_command(switch_command)
        time.sleep(0.05)  # Small delay between commands

def send_volume_command(ble_handler, volume_value):
    """Send volume control command to Boss Cube (legacy function)"""
    return send_parameter_command(ble_handler, PARAMETERS[0], volume_value)

class ParameterController:
    """Manages parameter selection and control"""
    def __init__(self):
        self.current_param_index = 0
        self.parameters = PARAMETERS
        self.last_selected_index = -1  # Track last selected to know when to switch effects
    
    def get_current_parameter(self) -> Parameter:
        return self.parameters[self.current_param_index]
    
    def next_parameter(self, ble_handler=None):
        self.current_param_index = (self.current_param_index + 1) % len(self.parameters)
        param = self.get_current_parameter()
        print(f"→ Selected: {param.name}")
        
        # Send effect switch commands if this parameter has them
        if ble_handler and param.effect_switch_commands:
            print(f"  Switching to {param.name.split()[-1]} effect...")
            send_effect_switch_commands(ble_handler, param)
        
        self.last_selected_index = self.current_param_index
    
    def prev_parameter(self, ble_handler=None):
        self.current_param_index = (self.current_param_index - 1) % len(self.parameters)
        param = self.get_current_parameter()
        print(f"← Selected: {param.name}")
        
        # Send effect switch commands if this parameter has them
        if ble_handler and param.effect_switch_commands:
            print(f"  Switching to {param.name.split()[-1]} effect...")
            send_effect_switch_commands(ble_handler, param)
        
        self.last_selected_index = self.current_param_index
    
    def set_parameter_value(self, ble_handler, pedal_value: int):
        """Set current parameter value from pedal (0-127)"""
        param = self.get_current_parameter()
        # Map pedal range (0-127) to parameter range
        param_value = int((pedal_value / 127.0) * param.max_val)
        param_value = max(param.min_val, min(param.max_val, param_value))
        
        success = send_parameter_command(ble_handler, param, param_value)
        if success:
            percentage = int((param_value / param.max_val) * 100)
            print(f"{param.name}: {param_value}/{param.max_val} ({percentage}%)")
        
        return success

def keyboard_test_mode(ble_handler):
    """Test mode using keyboard input with parameter navigation"""
    print("\n=== KEYBOARD TEST MODE ===")
    print("Commands:")
    print("  ← / →: Navigate parameters")
    print("  0-9: Set value (0=0%, 1=10%, 2=20%, ..., 9=90%)")
    print("  f: Set value to 100%")
    print("  q: Quit")
    print("Press Enter after each command...")
    
    controller = ParameterController()
    print(f"Current parameter: {controller.get_current_parameter().name}")
    
    while True:
        try:
            cmd = input("Command (←/→/0-9/f/q): ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd in ['←', 'left', 'a']:
                controller.prev_parameter(ble_handler)
            elif cmd in ['→', 'right', 'd']:
                controller.next_parameter(ble_handler)
            elif cmd == 'f':
                param = controller.get_current_parameter()
                send_parameter_command(ble_handler, param, param.max_val)
                print(f"{param.name}: {param.max_val}/{param.max_val} (100%)")
            elif cmd.isdigit() and 0 <= int(cmd) <= 9:
                param = controller.get_current_parameter()
                value = int((int(cmd) / 9.0) * param.max_val)  # Map 0-9 to parameter range
                send_parameter_command(ble_handler, param, value)
                percentage = int((value / param.max_val) * 100)
                print(f"{param.name}: {value}/{param.max_val} ({percentage}%)")
            else:
                print("Invalid command. Use ←/→ for navigation, 0-9/f for values, q to quit")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break

def find_ev1_pedal():
    """Find EV-1-WL pedal port automatically"""
    input_ports = mido.get_input_names()
    
    for port in input_ports:
        if "EV-1-WL" in port:
            return port
    
    return None

def main():
    """Main pedal control function with multi-parameter support"""
    print("Boss Cube II Multi-Parameter Control")
    print("=" * 40)
    
    # Check available MIDI ports
    print("Available MIDI Input Ports:")
    input_ports = mido.get_input_names()
    for port in input_ports:
        print(f"  - {port}")
    
    # Initialize BLE connection
    ble_handler = BLEMIDIHandler(DEVICE_ADDRESS)
    
    if not ble_handler.connect():
        print("Failed to connect to Boss Cube")
        print("Make sure the device is:")
        print("1. Powered on")
        print("2. In pairing/discoverable mode")
        print("3. Not connected to other devices")
        return
    
    try:
        # Test initial volume setting
        print("\nTesting parameter control...")
        controller = ParameterController()
        controller.set_parameter_value(ble_handler, 64)  # Set to 50%
        time.sleep(1)
        
        # Check if pedal is available
        pedal_port = find_ev1_pedal()
        if pedal_port:
            print(f"Found EV-1-WL pedal: {pedal_port}")
            print(f"Opening MIDI input: {pedal_port}")
            
            last_param_value = -1
            last_send_time = 0
            min_interval = 0.15
            
            print(f"\nCurrent parameter: {controller.get_current_parameter().name}")
            print("\nControls:")
            print("  Pedal (CC127): Adjust current parameter value")
            print("  Right Switch (CC80): Next parameter")
            print("  Left Switch (CC81): Previous parameter")
            print("  Press Ctrl+C to exit")
            
            with mido.open_input(pedal_port) as port:
                for msg in port:
                    current_time = time.time()
                    
                    if msg.type == 'control_change':
                        # Handle parameter navigation (footswitch)
                        if msg.control == 80 and msg.value == 127:  # Right switch pressed
                            controller.next_parameter(ble_handler)
                        elif msg.control == 81 and msg.value == 127:  # Left switch pressed
                            controller.prev_parameter(ble_handler)
                        
                        # Handle parameter value control (pedal)
                        elif msg.control == 127:
                            param = controller.get_current_parameter()
                            param_value = int((msg.value / 127.0) * param.max_val)
                            
                            # Only send if value changed and enough time has passed
                            if (param_value != last_param_value and 
                                current_time - last_send_time >= min_interval):
                                
                                controller.set_parameter_value(ble_handler, msg.value)
                                last_param_value = param_value
                                last_send_time = current_time
        else:
            print("EV-1-WL pedal not found!")
            print("Available MIDI ports:")
            for port in input_ports:
                print(f"  - {port}")
            print("Switching to keyboard test mode...")
            keyboard_test_mode(ble_handler)
                    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ble_handler.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main() 
