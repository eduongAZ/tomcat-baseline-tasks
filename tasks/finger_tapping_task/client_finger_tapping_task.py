import threading

import pygame
from common import UPDATE_RATE, receive, send

from .config_finger_tapping_task import BOX_WIDTH
from .utils import PlayerSquare


class ClientFingerTappingTask:
    def __init__(self, from_server, to_server, screen, client_name) -> None:
        self._from_server = from_server
        self._to_server = to_server
        self._screen = screen
        self._client_name = client_name

        self._state = None

        self._running = False

    def run(self):
        self._running = True

        client_input_thread = threading.Thread(target=self._client_input_handle, daemon=True)
        client_input_thread.start()

        print("[STATUS] Running client finger tapping task")

        win_width, win_height = pygame.display.get_surface().get_size()
        main_player_coordinate = ((win_width - BOX_WIDTH) / 2, (win_height / 2) - BOX_WIDTH - 1)
        other_player_height = (win_height / 2) + 1
        other_player_width_offset = (BOX_WIDTH / 2) + 1

        while self._running:
            pygame.event.get()

            data = receive([self._from_server], 0.0)
            if not data:
                continue
            else:
                [data] = data

            self._state = data["state"]

            num_other_players = len(self._state) - 1
            player_counter = 0

            self._screen.fill((0, 0, 0))

            # Add sprites to sprite group
            all_sprites_list = pygame.sprite.Group()
            for name, state in self._state.items():
                if name == self._client_name:
                    color = (255, 0, 255) if state else (100, 0, 100)
                    subject = PlayerSquare(main_player_coordinate, color)
                    all_sprites_list.add(subject)
                elif num_other_players == 1:
                    color = (255, 255, 255) if state else (100, 100, 100)
                    subject = PlayerSquare((main_player_coordinate[0], other_player_height), color)
                    all_sprites_list.add(subject)
                elif player_counter == 0:
                    color = (255, 255, 255) if state else (100, 100, 100)
                    subject = PlayerSquare((main_player_coordinate[0] - other_player_width_offset, other_player_height), color)
                    all_sprites_list.add(subject)
                    player_counter += 1
                else:
                    color = (255, 255, 255) if state else (100, 100, 100)
                    subject = PlayerSquare((main_player_coordinate[0] + other_player_width_offset, other_player_height), color)
                    all_sprites_list.add(subject)

            # Draw sprite group
            all_sprites_list.draw(self._screen)

            pygame.display.flip()

        # Wait for threads to finish
        client_input_thread.join()

    def _client_input_handle(self):
        """
        Send user's input command to server
        """
        clock = pygame.time.Clock()
        while self._running:
            # Get keys pressed by user
            keys = pygame.key.get_pressed()

            if self._state is None:
                continue

            data = None

            if keys[pygame.K_SPACE]:
                if self._state[self._client_name] == 0:
                    data = {}
                    data["type"] = "command"
                    data["sender"] = self._client_name
                    data["command"] = "tap"
            elif self._state[self._client_name] == 1:
                data = {}
                data["type"] = "command"
                data["sender"] = self._client_name
                data["command"] = "untap"

            if data is not None:
                send([self._to_server], data, wait_time=0.0)

            clock.tick(UPDATE_RATE)
