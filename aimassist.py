import pygame
import win32api
import win32con
import win32gui
import pyautogui
import cv2
import numpy as np

# =========================
# INIT
# =========================

pygame.init()

screen_w, screen_h = pyautogui.size()

screen = pygame.display.set_mode(
    (screen_w, screen_h),
    pygame.NOFRAME
)

pygame.display.set_caption("Training Overlay")

hwnd = pygame.display.get_wm_info()["window"]

# =========================
# WINDOW SETTINGS
# =========================

style = win32gui.GetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE
)

win32gui.SetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE,
    style |
    win32con.WS_EX_LAYERED |
    win32con.WS_EX_TOPMOST |
    win32con.WS_EX_TRANSPARENT
)

win32gui.SetLayeredWindowAttributes(
    hwnd,
    win32api.RGB(0, 0, 0),
    0,
    win32con.LWA_COLORKEY
)

font = pygame.font.SysFont("Arial", 60)

SCAN_SIZE = 400
LOCK_DISTANCE = 40

running = True

print("RIGHT CLICK = SCAN")
print("Q = EXIT")

# =========================
# LOOP
# =========================

while running:

    screen.fill((0, 0, 0))

    if win32api.GetAsyncKeyState(ord("Q")):
        running = False

    # ONLY ACTIVE ON RIGHT CLICK
    if win32api.GetKeyState(win32con.VK_RBUTTON) < 0:

        left = screen_w // 2 - SCAN_SIZE // 2
        top = screen_h // 2 - SCAN_SIZE // 2

        screenshot = pyautogui.screenshot(
            region=(left, top, SCAN_SIZE, SCAN_SIZE)
        )

        frame = np.array(screenshot)

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2BGR
        )

        hsv = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        # RED TARGET DETECTION
        lower_red1 = np.array([0,120,80])
        upper_red1 = np.array([10,255,255])

        lower_red2 = np.array([170,120,80])
        upper_red2 = np.array([180,255,255])

        mask1 = cv2.inRange(
            hsv,
            lower_red1,
            upper_red1
        )

        mask2 = cv2.inRange(
            hsv,
            lower_red2,
            upper_red2
        )

        mask = mask1 + mask2

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        best_distance = 999999

        center_x = SCAN_SIZE // 2
        center_y = SCAN_SIZE // 2

        for cnt in contours:

            area = cv2.contourArea(cnt)

            if area > 80:

                x, y, w, h = cv2.boundingRect(cnt)

                cx = x + w // 2
                cy = y + h // 2

                distance = (
                    (cx - center_x) ** 2 +
                    (cy - center_y) ** 2
                ) ** 0.5

                if distance < best_distance:
                    best_distance = distance

        # SHOW LOCK TEXT
        if (
            best_distance != 999999 and
            best_distance < LOCK_DISTANCE
        ):

            text = font.render(
                "TARGET LOCKED",
                True,
                (255, 0, 0)
            )

            rect = text.get_rect(
                center=(screen_w // 2, 120)
            )

            screen.blit(text, rect)

    pygame.display.update()

pygame.quit()