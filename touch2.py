import time
import busio
import board
import adafruit_mpr121
import pygame
import sys

# Configuration
I2C_ADDRESSES = [0x5a, 0x5c]
ELECTRODES_PER_SENSOR = 12
TOTAL_ELECTRODES = ELECTRODES_PER_SENSOR * len(I2C_ADDRESSES)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CIRCLE_RADIUS = 20
CIRCLE_MARGIN = 50
FPS = 30
# Debounce threshold in seconds (to filter ghost touches)
DEBOUNCE_THRESHOLD = 0.05  # e.g. 50 ms

# Physical layout mapping (one sensor pad is offline)
TOP_ROW = [1, 3, 5, 7, 9, 11, 16, 13, 17, 18, 20]
BOTTOM_ROW = [0, 2, 4, 6, 8, 10, 15, 12, 14, 21, 23, 22]


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
        base_index = sensor_index * ELECTRODES_PER_SENSOR
        for i in range(ELECTRODES_PER_SENSOR):
            if sensor[i].value:
                touched.append(base_index + i)
    return touched


def generate_electrode_positions():
    """Generate a dict mapping electrode index to (x, y) based on physical layout."""
    positions = {}
    # Calculate horizontal spacing for each row
    x_spacing_top = (WINDOW_WIDTH - 2 * CIRCLE_MARGIN) / (max(len(TOP_ROW) - 1, 1))
    x_spacing_bottom = (WINDOW_WIDTH - 2 * CIRCLE_MARGIN) / (max(len(BOTTOM_ROW) - 1, 1))

    # Fixed vertical positions
    y_top = CIRCLE_MARGIN
    y_bottom = WINDOW_HEIGHT - CIRCLE_MARGIN

    # Top row positions
    for i, idx in enumerate(TOP_ROW):
        x = CIRCLE_MARGIN + i * x_spacing_top
        positions[idx] = (int(x), int(y_top))

    # Bottom row positions
    for i, idx in enumerate(BOTTOM_ROW):
        x = CIRCLE_MARGIN + i * x_spacing_bottom
        positions[idx] = (int(x), int(y_bottom))

    return positions


def run_touch_visualizer():
    """Main loop: initialize, read touches, handle events, and display electrode states."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MPR121 Touch Visualizer")
    clock = pygame.time.Clock()

    sensors = initialize_mpr121_sensors(I2C_ADDRESSES)
    if not sensors:
        print("No MPR121 sensors found. Exiting.")
        pygame.quit()
        sys.exit(1)

    electrode_positions = generate_electrode_positions()

    # State tracking for debounce and events
    last_raw = {idx: False for idx in electrode_positions}
    debounced = {idx: False for idx in electrode_positions}
    last_change_time = {idx: time.time() for idx in electrode_positions}
    activation_time = {}

    running = True
    while running:
        now = time.time()
        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read raw touch input
        raw_touches = get_touched_electrodes(sensors)
        # Process each electrode for debounce
        for idx in electrode_positions:
            is_touched = idx in raw_touches
            if is_touched != last_raw[idx]:
                last_change_time[idx] = now
                last_raw[idx] = is_touched

            # If state has been stable beyond threshold
            if (now - last_change_time[idx]) >= DEBOUNCE_THRESHOLD:
                if is_touched and not debounced[idx]:
                    # Touch activated event
                    debounced[idx] = True
                    activation_time[idx] = now
                    print(f"Touch activated on electrode {idx}")
                elif not is_touched and debounced[idx]:
                    # Touch deactivated event
                    debounced[idx] = False
                    held_for = now - activation_time.get(idx, now)
                    print(f"Touch deactivated on electrode {idx} after {held_for:.3f}s hold")

        # Draw electrodes based on debounced state
        screen.fill((0, 0, 0))
        for idx, pos in electrode_positions.items():
            color = (0, 255, 0) if debounced[idx] else (50, 50, 50)
            pygame.draw.circle(screen, color, pos, CIRCLE_RADIUS)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_touch_visualizer()
