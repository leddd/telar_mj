import time
import busio
import board
import adafruit_mpr121
import sys

# Configuration
I2C_ADDRESSES = [0x5a, 0x5c]
ELECTRODES_PER_SENSOR = 12
# Debounce threshold in seconds (to filter ghost touches)
DEBOUNCE_THRESHOLD = 0.05  # 50 ms

# Physical layout mapping based on loom threads (left-to-right order)
#TOP_ROW = [1, 3, 5, 7, 9, 11, 16, 13, 17, 18, 20]    # 11 working pads, top row
#BOTTOM_ROW = [0, 2, 4, 6, 8, 10, 15, 12, 14, 21, 23, 22]  # 12 working pads, bottom row


TOP_ROW = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21] 
BOTTOM_ROW = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 23] 

ELECTRODE_INDICES = TOP_ROW + BOTTOM_ROW

def initialize_mpr121_sensors(addresses):
    """Initialize MPR121 sensors on the I2C bus."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensors = []
    for address in addresses:
        try:
            sensor = adafruit_mpr121.MPR121(i2c, address=address)
            sensors.append(sensor)
        except Exception as e:
            print(f"Failed to initialize MPR121 at address {hex(address)}: {e}")
    return sensors


def get_touched_electrodes(sensors):
    """Read touch status from each MPR121 and return a list of touched indices."""
    touched = []
    for sensor_index, sensor in enumerate(sensors):
        base = sensor_index * ELECTRODES_PER_SENSOR
        for i in range(ELECTRODES_PER_SENSOR):
            if sensor[i].value:
                touched.append(base + i)
    return touched


def main():
    sensors = initialize_mpr121_sensors(I2C_ADDRESSES)
    if not sensors:
        print("No MPR121 sensors found. Exiting.")
        sys.exit(1)

    # State tracking for debounce and events
    last_raw = {idx: False for idx in ELECTRODE_INDICES}
    debounced = {idx: False for idx in ELECTRODE_INDICES}
    last_change = {idx: time.time() for idx in ELECTRODE_INDICES}
    activation_time = {}

    print("Starting touch event logger (Ctrl+C to exit)")
    try:
        while True:
            now = time.time()
            raw = get_touched_electrodes(sensors)

            for idx in ELECTRODE_INDICES:
                is_touched = idx in raw
                # Detect raw state changes
                if is_touched != last_raw[idx]:
                    last_change[idx] = now
                    last_raw[idx] = is_touched

                # If stable beyond debounce threshold, fire events
                if (now - last_change[idx]) >= DEBOUNCE_THRESHOLD:
                    if is_touched and not debounced[idx]:
                        debounced[idx] = True
                        activation_time[idx] = now
                        print(f"Touch activated on electrode {idx}")
                    elif not is_touched and debounced[idx]:
                        debounced[idx] = False
                        hold = now - activation_time.get(idx, now)
                        print(f"Touch deactivated on electrode {idx} after {hold:.3f}s hold")

            time.sleep(0.01)  # small delay to limit CPU usage
    except KeyboardInterrupt:
        print("Exiting touch event logger.")


if __name__ == "__main__":
    main()
