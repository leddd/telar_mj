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
    if len(TOP_ROW) > 1:
        x_spacing_top = (WINDOW_WIDTH - 2 * CIRCLE_MARGIN) / (len(TOP_ROW) - 1)
    else:
        x_spacing_top = 0
    if len(BOTTOM_ROW) > 1:
        x_spacing_bottom = (WINDOW_WIDTH - 2 * CIRCLE_MARGIN) / (len(BOTTOM_ROW) - 1)
    else:
        x_spacing_bottom = 0

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
    """Main loop: initialize, read touches, and display electrode states."""
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
    previous_touches = []

    running = True
    while running:
        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read and debounce touch input
        current_touches = get_touched_electrodes(sensors)
        if current_touches != previous_touches:
            previous_touches = current_touches

        # Draw electrodes
        screen.fill((0, 0, 0))
        for idx, pos in electrode_positions.items():
            color = (0, 255, 0) if idx in current_touches else (50, 50, 50)
            pygame.draw.circle(screen, color, pos, CIRCLE_RADIUS)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_touch_visualizer()
