import time
import pygame
import sys

# Configuration
# Define 23 keys in left-to-right layout: 11 top row (numbers), 12 bottom row (letters)
top_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
            pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_MINUS]
bottom_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t,
               pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p,
               pygame.K_a, pygame.K_s]
# Map each key to a logical electrode index 0-22
key_map = {key: idx for idx, key in enumerate(top_keys + bottom_keys)}

# Debounce threshold in seconds
DEBOUNCE_THRESHOLD = 0.05


def main():
    pygame.init()
    # Needed to capture keyboard events\ n    screen = pygame.display.set_mode((200, 200))
    pygame.display.set_caption("Keyboard Touch Logger")
    print("Keyboard Touch Logger (Press ESC or close window to exit)")

    # State tracking
    debounced = {idx: False for idx in key_map.values()}
    last_change = {idx: time.time() for idx in key_map.values()}
    activation_time = {}

    running = True
    while running:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if event.key in key_map:
                    idx = key_map[event.key]
                    is_touched = (event.type == pygame.KEYDOWN)
                    # Debounce: register change only after threshold
                    if (now - last_change[idx]) >= DEBOUNCE_THRESHOLD:
                        last_change[idx] = now
                        if is_touched and not debounced[idx]:
                            debounced[idx] = True
                            activation_time[idx] = now
                            print(f"Touch activated on key idx {idx}")
                        elif not is_touched and debounced[idx]:
                            debounced[idx] = False
                            hold = now - activation_time.get(idx, now)
                            print(f"Touch deactivated on key idx {idx} after {hold:.3f}s hold")
        time.sleep(0.01)

    print("Exiting keyboard touch logger.")
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
