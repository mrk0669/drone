"""
chat_panel.py — In-simulation command chat panel for Drone2dEnv
================================================================
Adds a live text-input sidebar to the Pygame window.
Users can type commands to control the drone during simulation.

Supported commands:
  target <x> <y>     – Move the target to (x, y)
  reset              – Reset the episode
  force <l> <r>      – Override motor forces for the next step
  gravity <g>        – Change gravity (default 1000)
  pause              – Pause/unpause the simulation
  clear              – Clear the chat history
  help               – Show available commands
"""

import pygame
import textwrap

# ── Colours ──────────────────────────────────────────────────────────────────
BG_COLOR        = (20,  20,  30)
BORDER_COLOR    = (60,  120, 180)
INPUT_BG        = (30,  30,  45)
INPUT_ACTIVE_BG = (40,  40,  60)
TEXT_COLOR      = (220, 220, 220)
PROMPT_COLOR    = (100, 200, 255)
OUTPUT_COLOR    = (160, 230, 160)
ERROR_COLOR     = (255, 100, 100)
MUTED_COLOR     = (120, 120, 140)
CURSOR_COLOR    = (100, 200, 255)

PANEL_WIDTH     = 300
INPUT_HEIGHT    = 36
FONT_SIZE       = 14
LINE_HEIGHT     = 18
PADDING         = 10


class ChatPanel:
    """
    A Pygame sidebar panel with a command-line style chat interface.

    Usage
    -----
    panel = ChatPanel(screen_height=800)

    # Inside your event loop:
    consumed = panel.handle_event(event)   # returns True if event was consumed

    # After env.step():
    command = panel.get_pending_command()  # returns (cmd_name, args) or None
    panel.clear_pending_command()

    # Inside render:
    panel.draw(screen, x_offset)           # x_offset = sim_width
    """

    def __init__(self, screen_height: int = 800):
        pygame.font.init()
        self.height = screen_height
        self.width  = PANEL_WIDTH

        self.font        = pygame.font.SysFont("Consolas", FONT_SIZE)
        self.font_bold   = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
        self.font_small  = pygame.font.SysFont("Consolas", FONT_SIZE - 2)

        self.input_text  = ""
        self.history     = []          # list of (text, colour) tuples
        self.cursor_vis  = True
        self.cursor_tick = 0

        self._pending_command = None   # (cmd, args) waiting to be consumed
        self.paused = False
        self.force_override = None     # (left_force, right_force) or None

        self._add_line("Drone Chat Console", PROMPT_COLOR)
        self._add_line("Type 'help' for commands.", MUTED_COLOR)
        self._add_line("─" * 34, MUTED_COLOR)

    # ── Public API ────────────────────────────────────────────────────────────

    def handle_event(self, event) -> bool:
        """Process a pygame event. Returns True if the panel consumed it."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.key == pygame.K_ESCAPE:
                self.input_text = ""
                return True
            elif event.unicode and event.unicode.isprintable():
                self.input_text += event.unicode
                return True
        return False

    def get_pending_command(self):
        """Return the next queued command as (cmd_str, args_list) or None."""
        return self._pending_command

    def clear_pending_command(self):
        self._pending_command = None

    def draw(self, screen: pygame.Surface, x_offset: int):
        """Draw the panel starting at x_offset on the given surface."""
        # Background
        pygame.draw.rect(screen, BG_COLOR, (x_offset, 0, self.width, self.height))
        pygame.draw.line(screen, BORDER_COLOR, (x_offset, 0), (x_offset, self.height), 2)

        # Title bar
        title_surf = self.font_bold.render(" ◈  Drone Console", True, PROMPT_COLOR)
        screen.blit(title_surf, (x_offset + PADDING, 8))
        pygame.draw.line(screen, BORDER_COLOR,
                         (x_offset, 28), (x_offset + self.width, 28), 1)

        # History area (scrollable from bottom up)
        chat_area_top    = 32
        input_area_top   = self.height - INPUT_HEIGHT - PADDING
        chat_area_height = input_area_top - chat_area_top - PADDING

        # Clip to chat area
        chat_rect = pygame.Rect(x_offset + PADDING, chat_area_top,
                                self.width - PADDING*2, chat_area_height)

        # Render lines bottom-up
        y = chat_area_top + chat_area_height - LINE_HEIGHT
        for text, colour in reversed(self.history):
            wrapped = textwrap.wrap(text, width=30) or [""]
            for line in reversed(wrapped):
                if y < chat_area_top:
                    break
                surf = self.font_small.render(line, True, colour)
                screen.blit(surf, (x_offset + PADDING, y))
                y -= LINE_HEIGHT

        # Input box
        inp_rect = pygame.Rect(x_offset + PADDING,
                               input_area_top,
                               self.width - PADDING*2,
                               INPUT_HEIGHT)
        pygame.draw.rect(screen, INPUT_ACTIVE_BG, inp_rect, border_radius=4)
        pygame.draw.rect(screen, BORDER_COLOR, inp_rect, 1, border_radius=4)

        # Prompt symbol
        prompt_surf = self.font_bold.render(">", True, PROMPT_COLOR)
        screen.blit(prompt_surf, (inp_rect.x + 6, inp_rect.y + 9))

        # Input text + blinking cursor
        self.cursor_tick += 1
        if self.cursor_tick > 30:
            self.cursor_vis = not self.cursor_vis
            self.cursor_tick = 0

        display_text = self.input_text
        if self.cursor_vis:
            display_text += "█"

        text_surf = self.font.render(display_text, True, TEXT_COLOR)
        screen.blit(text_surf, (inp_rect.x + 20, inp_rect.y + 10))

        # Status badges
        badges = []
        if self.paused:
            badges.append(("⏸ PAUSED", (255, 200, 50)))
        if self.force_override:
            badges.append(("⚙ FORCE LOCK", (255, 120, 50)))

        bx = x_offset + PADDING
        by = self.height - INPUT_HEIGHT - PADDING*3 - 14
        for label, colour in badges:
            bsurf = self.font_small.render(label, True, colour)
            screen.blit(bsurf, (bx, by))
            bx += bsurf.get_width() + 12

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _add_line(self, text: str, colour=TEXT_COLOR):
        self.history.append((text, colour))

    def _submit(self):
        raw = self.input_text.strip()
        if not raw:
            return
        self._add_line(f"> {raw}", PROMPT_COLOR)
        self.input_text = ""
        self._parse(raw)

    def _parse(self, raw: str):
        parts = raw.lower().split()
        cmd   = parts[0]
        args  = parts[1:]

        if cmd == "help":
            for line in [
                "target <x> <y>  – set target",
                "reset           – reset episode",
                "force <l> <r>   – lock motor forces",
                "force off       – release force lock",
                "gravity <g>     – change gravity",
                "pause           – toggle pause",
                "clear           – clear console",
                "help            – show this help",
            ]:
                self._add_line("  " + line, MUTED_COLOR)

        elif cmd == "clear":
            self.history.clear()
            self._add_line("Console cleared.", MUTED_COLOR)

        elif cmd == "pause":
            self.paused = not self.paused
            self._add_line(f"Simulation {'paused' if self.paused else 'resumed'}.",
                           OUTPUT_COLOR)

        elif cmd == "target":
            if len(args) < 2:
                self._add_line("Usage: target <x> <y>", ERROR_COLOR)
                return
            try:
                x, y = float(args[0]), float(args[1])
                x = max(50, min(750, x))
                y = max(50, min(750, y))
                self._pending_command = ("target", [x, y])
                self._add_line(f"Target → ({x:.0f}, {y:.0f})", OUTPUT_COLOR)
            except ValueError:
                self._add_line("Error: x and y must be numbers.", ERROR_COLOR)

        elif cmd == "reset":
            self._pending_command = ("reset", [])
            self._add_line("Resetting episode…", OUTPUT_COLOR)

        elif cmd == "force":
            if args and args[0] == "off":
                self.force_override = None
                self._add_line("Force lock released.", OUTPUT_COLOR)
                return
            if len(args) < 2:
                self._add_line("Usage: force <left> <right>  |  force off",
                               ERROR_COLOR)
                return
            try:
                l, r = float(args[0]), float(args[1])
                self.force_override = (l, r)
                self._pending_command = ("force", [l, r])
                self._add_line(f"Forces locked → L={l:.0f} R={r:.0f}",
                               OUTPUT_COLOR)
            except ValueError:
                self._add_line("Error: forces must be numbers.", ERROR_COLOR)

        elif cmd == "gravity":
            if len(args) < 1:
                self._add_line("Usage: gravity <value>", ERROR_COLOR)
                return
            try:
                g = float(args[0])
                self._pending_command = ("gravity", [g])
                self._add_line(f"Gravity → {g:.0f}", OUTPUT_COLOR)
            except ValueError:
                self._add_line("Error: gravity must be a number.", ERROR_COLOR)

        else:
            self._add_line(f"Unknown command: '{cmd}'", ERROR_COLOR)
            self._add_line("Type 'help' for commands.", MUTED_COLOR)
