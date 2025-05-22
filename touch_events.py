import time
import busio
import board
import adafruit_mpr121
import sys

# Configuration
i2c_addresses = [0x5a, 0x5c]
electrodes_per_sensor = 12
# Debounce threshold in seconds (to filter ghost touches)
debounce_threshold = 0.05  # 50 ms

# Physical layout mapping based on loom threads (left-to-right order)
top_row = [1, 3, 5, 7, 9, 11, 16, 13, 17, 18, 20]    # 11 working pads, top row
bottom_row = [0, 2, 4, 6, 8, 10, 15, 12, 14, 21, 23, 22]  # 12 working pads, bottom row
electrode_indices = top_row + bottom_row

# remapping
remap = {
    16: 13,
    13: 15,
    18: 19,
    20: 21,
    15: 12,
    12: 14,
    14: 16,
    21: 18,
    23: 20,
}


def initialize_sensors(addresses):
    """Initialize MPR121 sensors on the I2C bus."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensors = []
    for addr in addresses:
        try:
            sensors.append(adafruit_mpr121.MPR121(i2c, address=addr))
        except Exception as e:
            print(f"Failed to init sensor at {hex(addr)}: {e}")
    return sensors


def get_touched(sensors):
    """Return a list of raw touched electrode indices."""
    touched = []
    for si, sensor in enumerate(sensors):
        base = si * electrodes_per_sensor
        for i in range(electrodes_per_sensor):
            if sensor[i].value:
                touched.append(base + i)
    return touched


def main():
    sensors = initialize_sensors(i2c_addresses)
    if not sensors:
        print("No sensors found. Exiting.")
        sys.exit(1)

    last_raw = {idx: False for idx in electrode_indices}
    debounced = {idx: False for idx in electrode_indices}
    last_change = {idx: time.time() for idx in electrode_indices}
    activation_time = {}

    print("Starting touch logger (Ctrl+C to exit)")
    try:
        while True:
            now = time.time()
            raw_touches = get_touched(sensors)

            for raw_idx in electrode_indices:
                touched = raw_idx in raw_touches
                if touched != last_raw[raw_idx]:
                    last_change[raw_idx] = now
                    last_raw[raw_idx] = touched

                if (now - last_change[raw_idx]) >= debounce_threshold:
                    # Apply remapping if defined
                    disp_idx = remap.get(raw_idx, raw_idx)
                    if touched and not debounced[raw_idx]:
                        debounced[raw_idx] = True
                        activation_time[raw_idx] = now
                        print(f"Touch activated on electrode {disp_idx}")
                    elif not touched and debounced[raw_idx]:
                        debounced[raw_idx] = False
                        hold = now - activation_time.get(raw_idx, now)
                        print(f"Touch deactivated on electrode {disp_idx} after {hold:.3f}s hold")

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Logger stopped.")

if __name__ == "__main__":
    main()

