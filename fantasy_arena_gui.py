
# Fantasy Arena: A Modular Battle Game -- FULL GUI VERSION

import os
import sys
from abc import ABC, abstractmethod
from enum import IntEnum

import pygame


# CONSTANTS
WINDOW_W, WINDOW_H = 1200, 700
TOP_BAR_H = 110
BOTTOM_BAR_H = 170

BAR_BG = (50, 50, 50)
BAR_GREEN = (60, 200, 90)
BAR_YELLOW = (230, 200, 60)
BAR_RED = (210, 60, 60)
TEXT_COLOR = (245, 245, 245)
PANEL_COLOR = (0, 0, 0, 160)          # semi-transparent black
BUTTON_COLOR = (30, 30, 40, 210)
BUTTON_HOVER = (70, 70, 110, 230)
BUTTON_BORDER = (200, 200, 220)

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
PLACEHOLDER_COLORS = {
    "full": (70, 140, 90),
    "hurt": (170, 150, 60),
    "critical": (170, 70, 60),
    "special": (90, 70, 170),
}

CHARACTER_NAMES = ["Gojo", "Sukuna", "Goku"]


# GAME LOGIC — characters, arena
class Environment(IntEnum):
    Fire = 0
    Ice = 1
    Jungle = 2


class Character(ABC):
    special_label = "Special Ability"

    def __init__(self, name="", level=0, health=0, attack=0, defence=0):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defence = defence

    def getHealth(self):
        return self.health

    def getAttack(self):
        return self.attack

    def getDefence(self):
        return self.defence

    def getname(self):
        return self.name

    def health_percent(self) -> float:
        if self.max_health <= 0:
            return 0.0
        return max(self.health, 0) / self.max_health * 100.0

    def health_stage(self) -> str:
        pct = self.health_percent()
        if pct <= 33:
            return "critical"
        elif pct <= 66:
            return "hurt"
        else:
            return "full"

    @abstractmethod
    def attackTarget(self, target: "Character"):
        pass

    @abstractmethod
    def heal(self):
        pass

    @abstractmethod
    def specialAbility(self):
        pass

    @abstractmethod
    def get_moves(self):
        pass

    def is_stronger_than(self, other: "Character") -> bool:
        s1 = s2 = 0
        s1, s2 = (s1 + 1, s2) if self.attack > other.attack else (s1, s2 + 1)
        s1, s2 = (s1 + 1, s2) if self.health > other.health else (s1, s2 + 1)
        s1, s2 = (s1 + 1, s2) if self.defence > other.defence else (s1, s2 + 1)
        s1, s2 = (s1 + 1, s2) if self.level > other.level else (s1, s2 + 1)
        return s1 > s2


class Gojo(Character):
    special_label = "Limitless: Six Eyes"

    def __init__(self):
        super().__init__("Gojo", 5, 80, 90, 70)

    def attackTarget(self, target):
        damage = max(self.getAttack() - target.getDefence(), 0)
        target.health = max(target.getHealth() - damage, 0)

    def heal(self):
        self.health += 40

    def specialAbility(self):
        self.attack += 50
        self.defence += 50

    def get_moves(self):
        return [
            ("Black Flash", "attack"),
            ("Reversal Blue", "attack"),
            ("Reverse Curse Technique", "heal"),
            ("Infinite Void", "special"),
        ]


class Sukuna(Character):
    special_label = "Malevolent Shrine"

    def __init__(self):
        super().__init__("Sukuna", 10, 75, 80, 75)

    def attackTarget(self, target):
        damage = max(self.getAttack() - target.getDefence(), 0)
        target.health = max(target.getHealth() - damage, 0)

    def heal(self):
        self.health += 35

    def specialAbility(self):
        self.attack += 45
        self.health += 50

    def get_moves(self):
        return [
            ("Black Flash", "attack"),
            ("Divine Flame", "attack"),
            ("Domain Amplification", "heal"),
            ("Domain Expansion", "special"),
        ]


class Goku(Character):
    special_label = "Super Saiyan"

    def __init__(self):
        super().__init__("Goku", 7, 50, 90, 70)

    def attackTarget(self, target):
        damage = max(self.getAttack() - target.getDefence(), 0)
        target.health = max(target.getHealth() - damage, 0)

    def heal(self):
        self.health += 50

    def specialAbility(self):
        self.level += 5
        self.attack += 90
        self.health += 70
        self.defence += 20

    def get_moves(self):
        return [
            ("Kamehameha", "attack"),
            ("Spirit Bomb", "attack"),
            ("Eat Senzu Bean", "heal"),
            ("Super Saiyan", "special"),
        ]


CHARACTER_CLASSES = {"Gojo": Gojo, "Sukuna": Sukuna, "Goku": Goku}


class Arena:
    def __init__(self, name="", env: Environment = None):
        self.name = name
        self.E = env

    def getEnvironment(self) -> str:
        mapping = {0: "Fire", 1: "Ice", 2: "Jungle"}
        return mapping.get(int(self.E), "Invalid")


# GUI HELPERS
def scale_cover(img: pygame.Surface, box_w: int, box_h: int) -> pygame.Surface:
    """Scale + crop an image to completely fill box_w x box_h (like CSS background-size: cover)."""
    iw, ih = img.get_size()
    scale = max(box_w / iw, box_h / ih)
    new_w, new_h = max(1, int(iw * scale) + 1), max(1, int(ih * scale) + 1)
    scaled = pygame.transform.smoothscale(img, (new_w, new_h))
    x = max(0, (new_w - box_w) // 2)
    y = max(0, (new_h - box_h) // 2)
    rect = pygame.Rect(x, y, box_w, box_h)
    rect.clamp_ip(scaled.get_rect())
    return scaled.subsurface(rect).copy()


class GUI:
    def __init__(self):
        global WINDOW_W, WINDOW_H
        pygame.init()
        # Launch fullscreen at the desktop's native resolution
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WINDOW_W, WINDOW_H = self.screen.get_size()
        pygame.display.set_caption("Fantasy Arena")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 46, bold=True)
        self.font_big = pygame.font.SysFont("arial", 30, bold=True)
        self.font_med = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 19)

        self._image_cache = {}

    # image loading 
    def _load_raw(self, name: str, stage: str) -> pygame.Surface:
        key = ("raw", name, stage)
        if key in self._image_cache:
            return self._image_cache[key]
        path = os.path.join(IMAGE_DIR, name, f"{stage}.png")
        surf = None
        if os.path.isfile(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
            except Exception:
                surf = None
        if surf is None:
            surf = pygame.Surface((600, 800))
            surf.fill(PLACEHOLDER_COLORS.get(stage, (100, 100, 100)))
            label = self.font_big.render(f"{name} [{stage}]", True, (255, 255, 255))
            surf.blit(label, label.get_rect(center=(300, 400)))
        self._image_cache[key] = surf
        return surf

    def get_side_image(self, name: str, stage: str) -> pygame.Surface:
        box_w, box_h = WINDOW_W // 2, WINDOW_H
        key = ("side", name, stage, box_w, box_h)
        if key in self._image_cache:
            return self._image_cache[key]
        raw = self._load_raw(name, stage)
        img = scale_cover(raw, box_w, box_h)
        self._image_cache[key] = img
        return img

    def get_full_image(self, name: str, stage: str, box_w: int, box_h: int) -> pygame.Surface:
        key = ("full", name, stage, box_w, box_h)
        if key in self._image_cache:
            return self._image_cache[key]
        raw = self._load_raw(name, stage)
        img = scale_cover(raw, box_w, box_h)
        self._image_cache[key] = img
        return img

    def check_quit(self, event):
        """Call at the top of every event loop: quits on window-close or Escape key
        (important since Escape is the only way out of fullscreen mode)."""
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    #  generic drawing
    def pump_or_quit(self):
        for event in pygame.event.get(pygame.QUIT):
            pygame.quit()
            sys.exit()

    def draw_panel(self, rect, color=PANEL_COLOR):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill(color)
        self.screen.blit(panel, rect.topleft)

    def draw_health_bar(self, x, y, w, h, pct):
        pygame.draw.rect(self.screen, BAR_BG, (x, y, w, h), border_radius=6)
        fill_w = int(w * max(pct, 0) / 100)
        color = BAR_GREEN if pct > 66 else (BAR_YELLOW if pct > 33 else BAR_RED)
        if fill_w > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_w, h), border_radius=6)
        pygame.draw.rect(self.screen, (10, 10, 10), (x, y, w, h), width=2, border_radius=6)

    def draw_battle_background(self, char1, char2, stage1_override=None, stage2_override=None):
        half_w = WINDOW_W // 2
        stage1 = stage1_override or (char1.health_stage() if char1 else "full")
        stage2 = stage2_override or (char2.health_stage() if char2 else "full")

        if char1:
            self.screen.blit(self.get_side_image(char1.name, stage1), (0, 0))
        else:
            self.screen.fill((25, 25, 35), pygame.Rect(0, 0, half_w, WINDOW_H))

        if char2:
            self.screen.blit(self.get_side_image(char2.name, stage2), (half_w, 0))
        else:
            self.screen.fill((25, 35, 25), pygame.Rect(half_w, 0, half_w, WINDOW_H))

        pygame.draw.line(self.screen, (10, 10, 10), (half_w, 0), (half_w, WINDOW_H), 4)

    def draw_top_bar(self, char1, char2, center_text=""):
        self.draw_panel(pygame.Rect(0, 0, WINDOW_W, TOP_BAR_H))
        half_w = WINDOW_W // 2

        if char1:
            name_surf = self.font_med.render(char1.name, True, TEXT_COLOR)
            self.screen.blit(name_surf, (30, 12))
            self.draw_health_bar(30, 50, 320, 22, char1.health_percent())
            hp_surf = self.font_small.render(
                f"HP {max(char1.getHealth(), 0)}/{char1.max_health}   ATK {char1.getAttack()}  DEF {char1.getDefence()}",
                True, TEXT_COLOR)
            self.screen.blit(hp_surf, (30, 78))

        if char2:
            name_surf = self.font_med.render(char2.name, True, TEXT_COLOR)
            self.screen.blit(name_surf, name_surf.get_rect(topright=(WINDOW_W - 30, 12)))
            self.draw_health_bar(WINDOW_W - 350, 50, 320, 22, char2.health_percent())
            hp_surf = self.font_small.render(
                f"HP {max(char2.getHealth(), 0)}/{char2.max_health}   ATK {char2.getAttack()}  DEF {char2.getDefence()}",
                True, TEXT_COLOR)
            self.screen.blit(hp_surf, hp_surf.get_rect(topright=(WINDOW_W - 30, 78)))

        if center_text:
            c_surf = self.font_small.render(center_text, True, (255, 230, 150))
            self.screen.blit(c_surf, c_surf.get_rect(center=(WINDOW_W // 2, 20)))

    def make_buttons(self, labels, y, width=280, height=58, gap=24):
        n = len(labels)
        total_w = n * width + (n - 1) * gap
        start_x = (WINDOW_W - total_w) // 2
        buttons = []
        for i, label in enumerate(labels):
            rect = pygame.Rect(start_x + i * (width + gap), y, width, height)
            buttons.append((rect, label))
        return buttons

    def draw_buttons(self, buttons):
        mouse_pos = pygame.mouse.get_pos()
        for i, (rect, label) in enumerate(buttons):
            hover = rect.collidepoint(mouse_pos)
            panel = pygame.Surface(rect.size, pygame.SRCALPHA)
            panel.fill(BUTTON_HOVER if hover else BUTTON_COLOR)
            self.screen.blit(panel, rect.topleft)
            pygame.draw.rect(self.screen, BUTTON_BORDER, rect, width=2, border_radius=10)
            label_text = f"{i + 1}. {label}"
            text_surf = self.font_small.render(label_text, True, TEXT_COLOR)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def draw_bottom_message(self, text, sub_text=""):
        rect = pygame.Rect(0, WINDOW_H - BOTTOM_BAR_H, WINDOW_W, BOTTOM_BAR_H)
        self.draw_panel(rect)
        msg_surf = self.font_big.render(text, True, TEXT_COLOR)
        self.screen.blit(msg_surf, msg_surf.get_rect(center=(WINDOW_W // 2, WINDOW_H - BOTTOM_BAR_H + 45)))
        if sub_text:
            sub_surf = self.font_small.render(sub_text, True, (210, 210, 210))
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_W // 2, WINDOW_H - 40)))

    #  blocking interaction helpers
    def select_option(self, prompt, labels, char1=None, char2=None, stage1=None, stage2=None,
                       top_text=""):
        """Draws image background + buttons, blocks until the user clicks a button
        or presses the matching number key. Returns the chosen index."""
        buttons = self.make_buttons(labels, WINDOW_H - BOTTOM_BAR_H + 95)
        while True:
            for event in pygame.event.get():
                self.check_quit(event)
                if event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(labels):
                            return idx
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, (rect, _label) in enumerate(buttons):
                        if rect.collidepoint(event.pos):
                            return i

            self.draw_battle_background(char1, char2, stage1, stage2)
            self.draw_top_bar(char1, char2, top_text)
            self.draw_bottom_message(prompt)
            self.draw_buttons(buttons)
            pygame.display.flip()
            self.clock.tick(30)

    def select_character(self, prompt):
        panel_w = WINDOW_W // 3
        while True:
            for event in pygame.event.get():
                self.check_quit(event)
                if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_3:
                    return CHARACTER_NAMES[event.key - pygame.K_1]
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = event.pos[0] // panel_w
                    if 0 <= idx < 3:
                        return CHARACTER_NAMES[idx]

            mouse_pos = pygame.mouse.get_pos()
            for i, name in enumerate(CHARACTER_NAMES):
                img = self.get_full_image(name, "full", panel_w, WINDOW_H)
                self.screen.blit(img, (i * panel_w, 0))

            for i in range(1, 3):
                pygame.draw.line(self.screen, (10, 10, 10), (i * panel_w, 0), (i * panel_w, WINDOW_H), 4)

            for i, name in enumerate(CHARACTER_NAMES):
                rect = pygame.Rect(i * panel_w, 0, panel_w, WINDOW_H)
                if rect.collidepoint(mouse_pos):
                    highlight = pygame.Surface((panel_w, WINDOW_H), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 40))
                    self.screen.blit(highlight, rect.topleft)
                label_bg = pygame.Rect(i * panel_w, WINDOW_H - 90, panel_w, 90)
                self.draw_panel(label_bg)
                name_surf = self.font_big.render(f"{i + 1}. {name}", True, TEXT_COLOR)
                self.screen.blit(name_surf, name_surf.get_rect(center=label_bg.center))

            title_bg = pygame.Rect(0, 0, WINDOW_W, 70)
            self.draw_panel(title_bg)
            title_surf = self.font_big.render(prompt, True, TEXT_COLOR)
            self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_W // 2, 35)))

            pygame.display.flip()
            self.clock.tick(30)

    def get_text_input(self, prompt, char1=None, char2=None):
        text = ""
        active = True
        while active:
            for event in pygame.event.get():
                self.check_quit(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if text.strip():
                            return text.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(text) < 30:
                        text += event.unicode

            self.draw_battle_background(char1, char2)
            self.draw_top_bar(char1, char2)
            self.draw_bottom_message(prompt, "Type the name, then press Enter")

            box = pygame.Rect(WINDOW_W // 2 - 220, WINDOW_H - BOTTOM_BAR_H + 95, 440, 46)
            self.draw_panel(box, (20, 20, 20, 220))
            pygame.draw.rect(self.screen, BUTTON_BORDER, box, width=2, border_radius=8)
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            text_surf = self.font_small.render(text + cursor, True, TEXT_COLOR)
            self.screen.blit(text_surf, text_surf.get_rect(midleft=(box.x + 12, box.centery)))

            pygame.display.flip()
            self.clock.tick(30)

    def show_message_wait(self, message, char1=None, char2=None, stage1=None, stage2=None, top_text=""):
        while True:
            for event in pygame.event.get():
                self.check_quit(event)
                if event.type == pygame.MOUSEBUTTONDOWN or (
                        event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)):
                    return

            self.draw_battle_background(char1, char2, stage1, stage2)
            self.draw_top_bar(char1, char2, top_text)
            self.draw_bottom_message(message, "Click or press Enter to continue")
            pygame.display.flip()
            self.clock.tick(30)

    def flash_special(self, message, char1, char2, special_side, duration_ms=1800):
        """Shows the special-ability image for the given side (1 or 2) for a set duration."""
        stage1 = "special" if special_side == 1 else None
        stage2 = "special" if special_side == 2 else None
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < duration_ms:
            for event in pygame.event.get():
                self.check_quit(event)
            self.draw_battle_background(char1, char2, stage1, stage2)
            self.draw_top_bar(char1, char2)
            self.draw_bottom_message(message)
            pygame.display.flip()
            self.clock.tick(30)


# ===========================================================
# GAME FLOW
# ===========================================================
def run_turn(gui: GUI, attacker: Character, defender: Character, side: int):
    moves = attacker.get_moves()
    labels = [m[0] for m in moves]

    idx = gui.select_option(
        f"{attacker.name}'s turn - choose your move",
        labels,
        char1=attacker if side == 1 else defender,
        char2=defender if side == 1 else attacker,
        top_text=f"{attacker.name}'s Turn",
    )
    label, move_type = moves[idx]

    if move_type == "attack":
        attacker.attackTarget(defender)
        gui.show_message_wait(f"{attacker.name} used {label}!")
    elif move_type == "heal":
        attacker.heal()
        gui.show_message_wait(f"{attacker.name} used {label} and recovered HP!")
    elif move_type == "special":
        gui.flash_special(f"{attacker.name} unleashes {attacker.special_label}!",
                           attacker if side == 1 else defender,
                           defender if side == 1 else attacker,
                           special_side=side)
        attacker.specialAbility()
        gui.show_message_wait(f"{attacker.name}'s stats have increased!")

        followup_moves = moves[:3]
        followup_labels = [m[0] for m in followup_moves]
        idx2 = gui.select_option(
            f"{attacker.name} - choose a follow-up move",
            followup_labels,
            char1=attacker if side == 1 else defender,
            char2=defender if side == 1 else attacker,
            top_text=f"{attacker.name}'s Turn",
        )
        label2, move_type2 = followup_moves[idx2]
        if move_type2 == "attack":
            attacker.attackTarget(defender)
            gui.show_message_wait(f"{attacker.name} used {label2}!")
        elif move_type2 == "heal":
            attacker.heal()
            gui.show_message_wait(f"{attacker.name} used {label2} and recovered HP!")


def main():
    gui = GUI()

    # ---- Character selection ----
    p1_name = gui.select_character("Player 1: Choose your fighter")
    p1 = CHARACTER_CLASSES[p1_name]()

    p2_name = gui.select_character("Player 2: Choose your fighter")
    p2 = CHARACTER_CLASSES[p2_name]()

    # ---- Arena setup ----
    arena_name = gui.get_text_input("Enter the name of the arena", p1, p2)

    env_idx = gui.select_option(
        "Choose the arena environment",
        ["Fire", "Ice", "Jungle"],
        char1=p1, char2=p2,
    )
    arena = Arena(arena_name, Environment(env_idx))

    # ---- Compare characters (optional) ----
    compare_idx = gui.select_option(
        "Compare characters before the fight?",
        ["Yes", "No"],
        char1=p1, char2=p2,
    )
    if compare_idx == 0:
        stronger = p1 if p1.is_stronger_than(p2) else p2
        gui.show_message_wait(f"{stronger.name} is the stronger character!", p1, p2)

    gui.show_message_wait(f"Welcome to {arena.name} ({arena.getEnvironment()} arena)!\n{p1.name} VS {p2.name}",
                           p1, p2)

    # ---- Battle loop ----
    turn = 2
    while True:
        turn = 1 if turn == 2 else 2
        if turn == 1:
            run_turn(gui, p1, p2, side=1)
        else:
            run_turn(gui, p2, p1, side=2)

        if p1.getHealth() <= 0:
            gui.show_message_wait(f"{p1.name} has been defeated! {p2.name} wins the battle!", p1, p2,
                                   stage1="critical", stage2="full")
            break
        if p2.getHealth() <= 0:
            gui.show_message_wait(f"{p2.name} has been defeated! {p1.name} wins the battle!", p1, p2,
                                   stage1="full", stage2="critical")
            break

    pygame.quit()


if __name__ == "__main__":
    main()