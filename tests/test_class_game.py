from unittest.mock import patch

import pytest

from cards.card import Card
from cards.game import Game
from cards.player import Player
from tests.config import comparison_lists_cards


class TestGame:
    @pytest.mark.parametrize(
        "player_hand, bot_hand, trump_suit, expected_player_move, "
        "expected_bot_move",
        [
            (
                [Card("9", "♦", 9, trump_card=True)],
                [Card("Валет", "♦", 11, trump_card=True)],
                "♦",
                True,
                False,
            ),
            (
                [Card("Валет", "♦", 11, trump_card=True)],
                [Card("9", "♦", 9, trump_card=True)],
                "♦",
                False,
                True,
            ),
            (
                [Card("Валет", "♦", 11, trump_card=True)],
                [Card("9", "♦", 9)],
                "♦",
                True,
                False,
            ),
            (
                [Card("9", "♥", 9)],
                [Card("Валет", "♦", 11, trump_card=True)],
                "♦",
                False,
                True,
            ),
        ],
    )
    def test_first_move(
        self, player_hand, bot_hand, trump_suit, expected_player_move,
            expected_bot_move
    ):
        # Создаём игроков
        player = Player("Player_1")
        player.hand = player_hand

        bot = Player("Bot")
        bot.hand = bot_hand

        game = Game()
        game.players = [player, bot]
        game.deck.set_trump(trump_suit)
        game.set_player_to_move_first()

        # Проверяем, что player ходит первый
        assert game.players[0].move == expected_player_move
        assert game.players[1].move == expected_bot_move


    def test_initialize_game(self):
        game = Game()
        game.initialize_game()

        assert len(game.players[0].hand) == 6
        assert isinstance(game.players[0].hand[0], Card)
        assert len(game.players[1].hand) == 6
        assert isinstance(game.players[1].hand[0], Card)
        assert len(game.deck.cards) == 24

    def test_user_input(self):
        game = Game()
        game.initialize_game()

        with patch("builtins.input", side_effect=["1"]):
            assert game.user_input() == 1
        with patch("builtins.input", side_effect=["8", "2"]):
            assert game.user_input() == 2
        with patch("builtins.input", side_effect=["d", "3"]):
            assert game.user_input() == 3

    @pytest.mark.parametrize(
        "player_hand, player_move, player_took_cards, bot_hand, bot_move, bot_took_cards,"
        " expected_player_hand, expected_player_move, expected_player_took_cards,"
        " expected_bot_hand, expected_bot_move, expected_bot_took_cards",
        [
            (
                [Card("6", "♦", 6, trump_card=True)],
                True,
                False,
                [Card("Валет", "♦", 11)],
                False,
                False,
                6,
                False,
                False,
                6,
                True,
                False,
            ),
            (
                [Card("7", "♦", 7, trump_card=True)],
                True,
                False,
                [Card("Дама", "♦", 12)],
                False,
                True,
                6,
                True,
                False,
                6,
                False,
                False,
            ),
            (
                [Card("8", "♦", 8, trump_card=True)],
                False,
                False,
                [Card("Кароль", "♦", 13)],
                True,
                False,
                6,
                True,
                False,
                6,
                False,
                False,
            ),
            (
                [Card("9", "♦", 9, trump_card=True)],
                False,
                True,
                [Card("Туз", "♦", 14)],
                True,
                False,
                6,
                False,
                False,
                6,
                True,
                False,
            ),
        ],
    )
    def test_next_turn(
        self,
        player_hand,
        player_move,
        player_took_cards,
        bot_hand,
        bot_move,
        bot_took_cards,
        expected_player_hand,
        expected_player_move,
        expected_player_took_cards,
        expected_bot_hand,
        expected_bot_move,
        expected_bot_took_cards,
    ):
        game = Game()

        player = Player("Player_1")
        player.hand = player_hand
        player.move = player_move
        player.took_cards = player_took_cards

        bot = Player("Bot")
        bot.hand = bot_hand
        bot.move = bot_move
        bot.took_cards = bot_took_cards

        game.players = [player, bot]

        game.next_turn()
        assert len(player.hand) == expected_player_hand
        assert player.move == expected_player_move
        assert player.took_cards == expected_player_took_cards
        assert len(bot.hand) == expected_bot_hand
        assert bot.move == expected_bot_move
        assert bot.took_cards == expected_bot_took_cards

    @pytest.mark.parametrize(
        "user_input_values",
        [
            (["0"]),
        ],
    )
    @patch.object(Game, "next_turn")
    def test_move_user(self, mock_next_turn, user_input_values):
        game = Game()

        # Настройка начального состояния игроков
        user = game.players[0]
        bot = game.players[1]

        # Установка начального состояния
        user.move = True
        bot.move = False
        bot.took_cards = True
        game.deck.cards_on_table = [Card("Кароль", "♦", 13)]

        # Функция, которая изменяет user.move на False
        def mock_input_side_effect(*args, **kwargs):
            user.move = False
            return user_input_values.pop(0)

        with patch("builtins.input", side_effect=mock_input_side_effect):
            game.move_user()

        # Проверка, что next_turn был вызван
        assert mock_next_turn.called

    @pytest.mark.parametrize(
        "card_hand, card_on_table, user_input, expected_card_on_table, length",
        [
            (
                [
                    Card("6", "♦", 6),
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11),
                    Card("7", "♣", 7),
                    Card("8", "♣", 8),
                    Card("10", "♥", 10),
                ],
                [],
                3,
                [Card("Валет", "♦", 11)],
                1,
            ),
            (
                [
                    Card("6", "♦", 6),
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11),
                    Card("7", "♣", 7),
                    Card("8", "♣", 8),
                    Card("10", "♥", 10),
                ],
                [Card("10", "♣", 10)],
                2,
                [Card("10", "♣", 10), Card("10", "♦", 10)],
                2,
            ),
            (
                [
                    Card("6", "♦", 6),
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11),
                    Card("7", "♣", 7),
                    Card("8", "♣", 8),
                    Card("10", "♥", 10),
                ],
                [Card("10", "♣", 10)],
                5,
                [Card("10", "♣", 10)],
                1,
            ),
        ],
    )
    def test_move_player_attack(
        self,
        card_hand,
        card_on_table,
        user_input,
        expected_card_on_table,
        length,
    ):
        game = Game()
        player = Player(name="Player_1")
        player.hand = card_hand
        game.players[0] = player
        game.deck.cards_on_table = card_on_table

        game.move_player_attack(user_input)

        assert len(game.deck.cards_on_table) == length
        comparison_lists_cards(game.deck.cards_on_table, expected_card_on_table)

    @pytest.mark.parametrize(
        "deck_cards, cards_table, card_hand, expected_cards_on_table, expected_len_hand,"
        " expected_len, expected_bot_took_cards",
        [
            (
                [Card("Валет", "♦", 11) for _ in range(20)],
                [Card("10", "♦", 10)],
                [
                    Card("6", "♦", 6),
                    Card("10", "♦", 10),
                    Card("Валет", "♥", 11),
                    Card("Валет", "♣", 11),
                    Card("Валет", "♦", 11),
                    Card("Дама", "♦", 12),
                ],
                [Card("10", "♦", 10), Card("Валет", "♦", 11)],
                5,
                2,
                False,
            ),
            (
                [Card("Валет", "♦", 11) for _ in range(20)],
                [Card("9", "♠", 9)],
                [
                    Card("6", "♦", 6),
                    Card("10", "♦", 10),
                    Card("Валет", "♥", 11),
                    Card("Валет", "♣", 11),
                    Card("Валет", "♦", 11),
                    Card("Дама", "♦", 12),
                ],
                [Card("9", "♠", 9)],
                6,
                1,
                True,
            ),
            (
                [Card("Валет", "♦", 11) for _ in range(10)],
                [Card("10", "♠", 10)],
                [
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11, trump_card=True),
                    Card("6", "♦", 6, trump_card=True),
                    Card("Валет", "♥", 11),
                    Card("Валет", "♣", 11),
                    Card("9", "♠", 9),
                ],
                [
                    Card("10", "♠", 10),
                    Card("6", "♦", 6, trump_card=True),
                ],
                5,
                2,
                False,
            ),
            (
                [Card("Валет", "♦", 11) for _ in range(3)],
                [Card("Валет", "♠", 11)],
                [
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11, trump_card=True),
                    Card("6", "♦", 6, trump_card=True),
                    Card("Валет", "♥", 11),
                    Card("Валет", "♣", 11),
                    Card("9", "♠", 9),
                ],
                [
                    Card("Валет", "♠", 11),
                    Card("Валет", "♦", 11, trump_card=True),
                ],
                5,
                2,
                False,
            ),
            (
                [Card("Валет", "♦", 11) for _ in range(3)],
                [Card("Дама", "♠", 12)],
                [
                    Card("Валет", "♣", 11),
                    Card("9", "♠", 9),
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11),
                    Card("6", "♦", 6),
                    Card("Валет", "♥", 11),
                ],
                [Card("Дама", "♠", 12)],
                6,
                1,
                True,
            ),
            (
                [Card("Валет", "♦", 11) for _ in range(3)],
                [Card("Дама", "♠", 12, trump_card=True)],
                [
                    Card("Валет", "♣", 11),
                    Card("9", "♠", 9),
                    Card("10", "♦", 10),
                    Card("Валет", "♦", 11, trump_card=True),
                    Card("6", "♦", 6),
                    Card("Кароль", "♥", 13, True),
                ],
                [
                    Card("Дама", "♠", 12, trump_card=True),
                    Card("Кароль", "♥", 13, True),
                ],
                5,
                2,
                False,
            ),
        ],
    )
    def test_move_bot_defense(
        self,
        deck_cards,
        cards_table,
        card_hand,
        expected_cards_on_table,
        expected_len_hand,
        expected_len,
        expected_bot_took_cards,
    ):
        game = Game()
        bot = Player("Bot")
        bot.hand = card_hand
        game.deck.cards_on_table = cards_table
        game.players[1] = bot
        game.deck.cards = deck_cards

        game.move_bot_defense()

        assert len(game.deck.cards_on_table) == expected_len
        assert len(bot.hand) == expected_len_hand
        comparison_lists_cards(
            game.deck.cards_on_table, expected_cards_on_table
        )
        assert bot.took_cards == expected_bot_took_cards
