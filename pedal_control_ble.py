#!/usr/bin/env python3
"""
This script is an abandoned prototype for controlling a Boss Cube II amplifier using BLE MIDI pedal (EV-1-WL).
Now it is replaced by the web-control project: https://github.com/PetrDlouhy/boss-web-control (which works on Android, but not on Linux due to problems with Bluez stack).

It still could be useful for understanding how to control the amplifier via BLE MIDI and how to access it on Linux.
Proble with Linux at the moment (2025-07-06) is, that the BlueZ stack doesn't recognize the right characteristics of Boss MIDI devices.
The only option is to use gatttool.

It allows for multi-parameter control, including volume, reverb, and various effects.

It uses gatttool for BLE communication and mido for MIDI handling, altough the end goal is to use some simpler, more relieable way like `mido`, but `mido` doesn't send the correct handlery yet.

This script is now more a prototype than a working thing.
"""
import mido
import subprocess
import time
import sys
import threading
import re
from typing import Optional, List, Tuple

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
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f, 0x7c]  # Effect activation with 7c
    ]),
    Parameter("Guitar Chorus Level", [0x10, 0x00, 0x00, 0x43], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x00],  # Switch to chorus
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f, 0x7c]  # Effect activation with 7c
    ]),
    Parameter("Guitar Tremolo Level", [0x10, 0x00, 0x00, 0x57], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x03],  # Switch to tremolo
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f, 0x7c]  # Effect activation with 7c
    ]),
    Parameter("Guitar T.WAH Level", [0x10, 0x00, 0x00, 0x5e], 0, 100, [
        [0x10, 0x00, 0x00, 0x39, 0x04],  # Switch to T.WAH
        [0x7f, 0x01, 0x02, 0x04, 0x7f, 0x7f, 0x7c]  # Effect activation with 7c
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
    # BLE MIDI format: 90 <timestamp> f0 <sysex_data> <timestamp> f7
    # Based on hex dump: 90 b7 f0 41 10 00 00 00 00 09 12 10 00 00 39 00 37 b7 f7
    gatt_header = "90"
    timestamp = "b7"  # This can vary but b7 is commonly used
    sysex_start = "f0"
    sysex_body = "".join(f"{b:02x}" for b in sysex_data)
    
    # Format: 90 <timestamp> f0 <sysex_data> <timestamp> f7
    complete_command = gatt_header + timestamp + sysex_start + sysex_body + timestamp + "f7"
    
    return complete_command

class BLEMIDIHandler:
    """Simple BLE MIDI handler using gatttool with improved reliability"""
    
    def __init__(self, device_address: str):
        self.device_address = device_address
        self.characteristic_handle = "0x000c"
        self.process = None
        self.is_connected = False
        self.output_buffer = []
        self.output_thread = None
        self.max_retries = 3
    
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
    

    
    def _try_gatttool_connection(self) -> bool:
        """Attempt a single gatttool connection"""
        try:
            if self.process:
                self.cleanup()
            
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
            
            # Wait for connection with timeout
            connection_timeout = 8
            start_time = time.time()
            
            while (time.time() - start_time) < connection_timeout:
                if self.process.poll() is not None:
                    return False
                
                # Check for connection success in output
                for line in self.output_buffer:
                    if "Connection successful" in line:
                        self.is_connected = True
                        print("✓ GATT connection established")
                        time.sleep(0.5)  # Let connection stabilize
                        
                        # Enable notifications - based on your hex dump, handle 0x001b was receiving notifications
                        print("📡 Enabling notifications on handle 0x000d (CCCD for 0x000c)...")
                        self.process.stdin.write("char-write-req 0x000d 0100\n")
                        self.process.stdin.flush()
                        time.sleep(0.3)
                        
                        # Check if notification enabling worked
                        for line in self.output_buffer[-3:]:
                            if "Characteristic value was written successfully" in line:
                                print("✓ Notification descriptor written successfully")
                                break
                        else:
                            print("⚠️  Notification descriptor write may have failed")
                        
                        # Test with a simple volume command to see if we get notifications
                        print("🧪 Testing notifications with a volume command...")
                        test_cmd = f"char-write-req {self.characteristic_handle} 90b7f04110000000000912200000043200b7f7\n"
                        self.process.stdin.write(test_cmd)
                        self.process.stdin.flush()
                        time.sleep(0.5)
                        
                        # Look for any notifications from the test
                        test_notifications = 0
                        for line in self.output_buffer[-10:]:
                            if "Notification handle" in line:
                                test_notifications += 1
                                print(f"🔔 Test notification: {line}")
                        
                        if test_notifications > 0:
                            print(f"✅ Notifications working! Received {test_notifications} test responses")
                        else:
                            print("❌ No notifications received during test - notifications may not be working")
                        
                        return True
                    elif "Connection failed" in line or "Can't connect" in line or "Device or resource busy" in line:
                        return False
                
                time.sleep(0.1)
            
            return False
                
        except Exception as e:
            print(f"gatttool connection error: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to device using gatttool - simple and straightforward"""
        print(f"Establishing GATT connection to {self.device_address}...")
        
        # Try gatttool connection with minimal retries
        for attempt in range(2):  # Just 2 attempts
            print(f"GATT connection attempt {attempt + 1}/2")
            
            if self._try_gatttool_connection():
                return True
            
            print(f"GATT connection failed on attempt {attempt + 1}")
            if attempt < 1:  # Only one retry
                time.sleep(2)
        
        print("✗ Failed to establish GATT connection")
        return False
    
    def send_command_fast(self, command_hex: str) -> bool:
        """Send BLE MIDI command - fast, no response for frequent commands (volume/levels)"""
        if not self.is_connected or not self.process:
            return False
        
        try:
            # Use char-write-cmd (no response) for fast commands
            cmd = f"char-write-cmd {self.characteristic_handle} {command_hex}\n"
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
            
            # Minimal wait for command to be sent
            time.sleep(0.05)  # Even faster since no response expected
            return True
            
        except Exception as e:
            print(f"Send command error: {e}")
            return False
    
    def send_command_blocking(self, command_hex: str) -> bool:
        """Send BLE MIDI command and wait for cube response - for mode switching"""
        if not self.is_connected or not self.process:
            return False
        
        try:
            # Clear output buffer before sending to get fresh responses
            buffer_size_before = len(self.output_buffer)
            
            cmd = f"char-write-req {self.characteristic_handle} {command_hex}\n"
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
            
            # Wait for cube response
            time.sleep(0.3)  # Longer wait to ensure we catch responses
            
            # Look for NEW lines since we sent the command
            response_count = 0
            notification_count = 0
            
            # Check all lines since the command was sent
            for line in self.output_buffer[buffer_size_before:]:
                if "Notification handle" in line:
                    notification_count += 1
                    if "value:" in line:
                        response_count += 1
                        hex_data = line.split("value:")[-1].strip()
                        print(f"🔔 Cube response: {hex_data}")
                    else:
                        print(f"🔔 Cube notification: {line}")
            
            if response_count > 0:
                print(f"✓ Received {response_count} data response(s) from cube")
            elif notification_count > 0:
                print(f"✓ Received {notification_count} notification(s) from cube (no data)")
            else:
                print("⚠️ No cube responses detected")
                # Debug: show recent output buffer
                print("📋 Recent gatttool output:")
                for line in self.output_buffer[buffer_size_before:]:
                    print(f"   {line}")
            
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
        self.is_connected = False
        
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

def send_parameter_command(handler, parameter: Parameter, value: int):
    """Send parameter control command to Boss Cube (value only) - fast for frequent pedal changes"""
    # Clamp value to parameter range
    value = max(parameter.min_val, min(parameter.max_val, value))
    parameter.current_value = value
    
    # Send parameter value command only (no effect switching)
    data = [value]
    checksum = roland_checksum(parameter.address + data)
    syx = BOSS_CUBE_HEADER + parameter.address + data + [checksum]
    
    return handler.send_command_fast(syx)

def send_effect_switch_commands(handler, parameter: Parameter):
    """Send effect switch commands for a parameter - blocking with cube response"""
    print(f"  → Switching effect (sending {len(parameter.effect_switch_commands)} commands)...")
    
    for i, switch_cmd in enumerate(parameter.effect_switch_commands):
        # Add checksum to switch command
        checksum = roland_checksum(switch_cmd)
        switch_syx = BOSS_CUBE_HEADER + switch_cmd + [checksum]
        
        print(f"    Command {i+1}: Switching mode...")
        # Send the command with blocking (waits for cube response)
        success = handler.send_command_blocking(switch_syx)
        if not success:
            print(f"    ✗ Command {i+1} failed")
            return False
        
        # Small delay between commands for effect switching
        time.sleep(0.1)
    
    print(f"  ✓ Effect switch completed")
    return True

def send_volume_command(handler, volume_value):
    """Send volume control command to Boss Cube (legacy function)"""
    return send_parameter_command(handler, PARAMETERS[0], volume_value)

class ParameterController:
    """Manages parameter selection and control"""
    def __init__(self):
        self.current_param_index = 0
        self.parameters = PARAMETERS
        self.last_selected_index = -1  # Track last selected to know when to switch effects
    
    def get_current_parameter(self) -> Parameter:
        return self.parameters[self.current_param_index]
    
    def next_parameter(self, handler=None):
        self.current_param_index = (self.current_param_index + 1) % len(self.parameters)
        param = self.get_current_parameter()
        print(f"→ Selected: {param.name}")
        
        # Send effect switch commands if this parameter has them
        if handler and param.effect_switch_commands:
            print(f"  Switching to {param.name.split()[-1]} effect...")
            success = send_effect_switch_commands(handler, param)
            if not success:
                print(f"  ✗ Failed to switch to {param.name.split()[-1]} effect")
        
        self.last_selected_index = self.current_param_index
    
    def prev_parameter(self, handler=None):
        self.current_param_index = (self.current_param_index - 1) % len(self.parameters)
        param = self.get_current_parameter()
        print(f"← Selected: {param.name}")
        
        # Send effect switch commands if this parameter has them
        if handler and param.effect_switch_commands:
            print(f"  Switching to {param.name.split()[-1]} effect...")
            success = send_effect_switch_commands(handler, param)
            if not success:
                print(f"  ✗ Failed to switch to {param.name.split()[-1]} effect")
        
        self.last_selected_index = self.current_param_index
    
    def set_parameter_value(self, handler, pedal_value: int):
        """Set current parameter value from pedal (0-127)"""
        param = self.get_current_parameter()
        # Map pedal range (0-127) to parameter range
        param_value = int((pedal_value / 127.0) * param.max_val)
        param_value = max(param.min_val, min(param.max_val, param_value))
        
        success = send_parameter_command(handler, param, param_value)
        if success:
            percentage = int((param_value / param.max_val) * 100)
            print(f"{param.name}: {param_value}/{param.max_val} ({percentage}%)")
        
        return success

def keyboard_test_mode(handler):
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
                controller.prev_parameter(handler)
            elif cmd in ['→', 'right', 'd']:
                controller.next_parameter(handler)
            elif cmd == 'f':
                param = controller.get_current_parameter()
                send_parameter_command(handler, param, param.max_val)
                print(f"{param.name}: {param.max_val}/{param.max_val} (100%)")
            elif cmd.isdigit() and 0 <= int(cmd) <= 9:
                param = controller.get_current_parameter()
                value = int((int(cmd) / 9.0) * param.max_val)  # Map 0-9 to parameter range
                send_parameter_command(handler, param, value)
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

def run_bluetooth_command(command: List[str], timeout: int = 10) -> Tuple[bool, str]:
    """Run a bluetooth command and return success status and output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timeout"
    except Exception as e:
        return False, str(e)

def bluetooth_disconnect(device_address: str) -> bool:
    """Disconnect device via bluetoothctl"""
    print(f"Disconnecting {device_address}...")
    success, output = run_bluetooth_command(["bluetoothctl", "disconnect", device_address], 5)
    time.sleep(1)  # Give time for disconnection
    return success

def find_cube_midi_port():
    """Find Boss Cube MIDI port (for detection only, not control)"""
    input_ports = mido.get_input_names()
    output_ports = mido.get_output_names()
    
    for port in output_ports:
        if "CUBE-ST2" in port and "MIDI" in port:
            return port
    
    return None

class SimpleBossCubeHandler:
    """Simple Boss Cube handler - just disconnects ALSA if needed, then connects via GATT"""
    
    def __init__(self, device_address: str):
        self.device_address = device_address
        self.ble_handler = None
    
    def check_alsa_midi_connected(self) -> bool:
        """Check if Boss Cube is connected via ALSA MIDI"""
        return find_cube_midi_port() is not None
    
    def disconnect_alsa_midi(self) -> bool:
        """Disconnect Boss Cube from system Bluetooth to free it for GATT"""
        print("Boss Cube is connected via ALSA MIDI")
        print("ALSA MIDI doesn't support Boss Cube control commands")
        print("Disconnecting from system Bluetooth to enable GATT control...")
        
        success = bluetooth_disconnect(self.device_address)
        if success:
            # Wait for ALSA MIDI port to disappear
            for i in range(10):  # Wait up to 5 seconds
                time.sleep(0.5)
                if not self.check_alsa_midi_connected():
                    print("✓ Successfully disconnected from ALSA MIDI")
                    return True
                print(f"  Waiting for ALSA disconnection... ({i+1}/10)")
        
        print("✗ Failed to disconnect from ALSA MIDI")
        return False
    
    def connect(self) -> bool:
        """Connect via GATT, disconnecting from ALSA if necessary"""
        print("Detecting Boss Cube connection method...")
        
        # Check if ALSA MIDI is active and disconnect if needed
        if self.check_alsa_midi_connected():
            if not self.disconnect_alsa_midi():
                print("Cannot proceed - ALSA MIDI is active and can't be disconnected")
                return False
        
        print("Attempting GATT connection...")
        print("Note: Boss Cube should be discoverable (flashing Bluetooth LED)")
        
        # Connect via GATT
        self.ble_handler = BLEMIDIHandler(self.device_address)
        if self.ble_handler.connect():
            print("✓ GATT connection established for control commands")
            return True
        
        return False
    
    def send_command_fast(self, sysex_data: List[int]) -> bool:
        """Send command using GATT connection - fast for frequent commands"""
        if self.ble_handler:
            command = create_ble_midi_command(sysex_data)
            return self.ble_handler.send_command_fast(command)
        return False
    
    def send_command_blocking(self, sysex_data: List[int]) -> bool:
        """Send command using GATT connection - blocking for mode switches"""
        if self.ble_handler:
            command = create_ble_midi_command(sysex_data)
            return self.ble_handler.send_command_blocking(command)
        return False
    
    def disconnect(self):
        """Disconnect from GATT"""
        if self.ble_handler:
            self.ble_handler.disconnect()
        print("✓ Disconnected from GATT")
    
    def get_connection_info(self) -> str:
        """Get info about current connection"""
        if self.ble_handler:
            return f"GATT via {self.device_address} (control-capable)"
        return "Not connected"

def main():
    """Main pedal control function with GATT-based control"""
    print("Boss Cube II Multi-Parameter Control")
    print("=" * 40)
    
    # Check if bluetoothctl is available
    success, _ = run_bluetooth_command(["which", "bluetoothctl"])
    if not success:
        print("ERROR: bluetoothctl not found. Please install bluez-utils package.")
        print("This is required for Boss Cube control.")
        return
    
    # Check available MIDI ports
    print("\nAvailable MIDI Input Ports:")
    input_ports = mido.get_input_names()
    if not input_ports:
        print("  None found")
    else:
        for port in input_ports:
            print(f"  - {port}")
    
    print("\nAvailable MIDI Output Ports:")
    output_ports = mido.get_output_names()
    if not output_ports:
        print("  None found")
    else:
        for port in output_ports:
            print(f"  - {port}")
    
    # Initialize connection - always use GATT for control
    print(f"\nInitializing Boss Cube control connection...")
    print("Note: Only GATT connection supports Boss Cube parameter control")
    
    handler = SimpleBossCubeHandler(DEVICE_ADDRESS)
    
    if not handler.connect():
        print("\n" + "="*50)
        print("CONNECTION FAILED")
        print("="*50)
        print("Troubleshooting steps:")
        print("1. Ensure Boss Cube is powered on and in Bluetooth mode")
        print("2. If Cube is connected in system Bluetooth, script will try to disconnect it")
        print("3. Make sure Boss Cube is discoverable (flashing Bluetooth LED)")
        print("4. Power cycle the Boss Cube if connection keeps failing")
        print("5. Ensure Cube is not connected to phone/tablet")
        return
    
    print("\n" + "="*50)
    print("CONNECTION SUCCESSFUL!")
    print(f"Method: {handler.get_connection_info()}")
    print("="*50)
    
    try:
        # Test initial parameter control
        print("\nTesting parameter control...")
        controller = ParameterController()
        controller.set_parameter_value(handler, 64)  # Set to 50%
        time.sleep(0.2)
        
        # Initialize timer variable for cleanup
        final_value_timer = None
        
        # Check if pedal is available
        pedal_port = find_ev1_pedal()
        if pedal_port:
            print(f"\n✓ Found EV-1-WL pedal: {pedal_port}")
            print(f"Opening MIDI input: {pedal_port}")
            
            last_param_value = -1
            last_send_time = 0
            min_interval = 0.15  # GATT timing
            
            # Final value debouncing
            pending_final_value = None
            final_value_delay = 0.3  # Send final value 300ms after movement stops
            
            def send_final_value():
                """Send the final pedal value after movement stops"""
                nonlocal last_param_value, last_send_time, pending_final_value
                if pending_final_value is not None:
                    param = controller.get_current_parameter()
                    param_value = int((pending_final_value / 127.0) * param.max_val)
                    
                    # Only send if it's different from last sent value
                    if param_value != last_param_value:
                        print(f"🎯 Final: {param.name}: {param_value}/{param.max_val} ({int(param_value/param.max_val*100)}%)")
                        controller.set_parameter_value(handler, pending_final_value)
                        last_param_value = param_value
                        last_send_time = time.time()
                    
                    pending_final_value = None
            
            print(f"\nCurrent parameter: {controller.get_current_parameter().name}")
            print(f"Connection method: {handler.get_connection_info()}")
            print("\n" + "="*50)
            print("CONTROLS")
            print("="*50)
            print("🎚️  Pedal (CC127): Adjust current parameter value")
            print("➡️  Right Switch (CC80): Next parameter")
            print("⬅️  Left Switch (CC81): Previous parameter")
            print("⏹️  Press Ctrl+C to exit")
            print("="*50)
            
            with mido.open_input(pedal_port) as port:
                for msg in port:
                    current_time = time.time()
                    
                    if msg.type == 'control_change':
                        # Handle parameter navigation (footswitch)
                        if msg.control == 80 and msg.value == 127:  # Right switch pressed
                            controller.next_parameter(handler)
                        elif msg.control == 81 and msg.value == 127:  # Left switch pressed
                            controller.prev_parameter(handler)
                        
                        # Handle parameter value control (pedal)
                        elif msg.control == 127:
                            param = controller.get_current_parameter()
                            param_value = int((msg.value / 127.0) * param.max_val)
                            
                            # Always update pending final value
                            pending_final_value = msg.value
                            
                            # Cancel previous final value timer
                            if final_value_timer:
                                final_value_timer.cancel()
                            
                            # Send immediate value if enough time has passed
                            if (param_value != last_param_value and 
                                current_time - last_send_time >= min_interval):
                                
                                controller.set_parameter_value(handler, msg.value)
                                last_param_value = param_value
                                last_send_time = current_time
                                pending_final_value = None  # Clear pending since we just sent it
                            else:
                                # Schedule final value to be sent after delay
                                import threading
                                final_value_timer = threading.Timer(final_value_delay, send_final_value)
                                final_value_timer.start()
        else:
            print("\n⚠️  EV-1-WL pedal not found!")
            print("Available MIDI ports:")
            for port in input_ports:
                print(f"  - {port}")
            print("\nSwitching to keyboard test mode...")
            keyboard_test_mode(handler)
                    
    except KeyboardInterrupt:
        print("\n\nExiting gracefully...")
    except Exception as e:
        print(f"\nError during operation: {e}")
        print("This might be a connection issue. Try restarting the script.")
    finally:
        print("Cleaning up...")
        
        # Clean up final value timer if it exists
        try:
            if final_value_timer:
                final_value_timer.cancel()
        except:
            pass
        
        handler.disconnect()
        print("✓ Disconnected successfully")
        print("Thank you for using Boss Cube II Control!")

if __name__ == "__main__":
    main() 
