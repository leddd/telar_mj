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

def compute_electrode_positions(total, width, height, margin):
    """Compute (x, y) positions for each electrode in a grid layout."""
    columns = 6
    rows = (total + columns - 1) // columns
    x_spacing = (width - 2 * margin) / (columns - 1)
    y_spacing = (height - 2 * margin) / (rows - 1)
    positions = []
    for idx in range(total):
        row = idx // columns
        col = idx % columns
        x = margin + col * x_spacing
        y = margin + row * y_spacing
        positions.append((int(x), int(y)))
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

    electrode_positions = compute_electrode_positions(
        TOTAL_ELECTRODES, WINDOW_WIDTH, WINDOW_HEIGHT, CIRCLE_MARGIN
    )
    previous_touches = []

    running = True
    while running:
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read touch input
        current_touches = get_touched_electrodes(sensors)
        # Only update when touch state changes
        if current_touches != previous_touches:
            previous_touches = current_touches

        # Draw the electrodes
        screen.fill((0, 0, 0))
        for idx, pos in enumerate(electrode_positions):
            color = (0, 255, 0) if idx in current_touches else (50, 50, 50)
            pygame.draw.circle(screen, color, pos, CIRCLE_RADIUS)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_touch_visualizer()
