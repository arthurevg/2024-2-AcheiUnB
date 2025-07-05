# users/tests/test_match.py
from unittest.mock import MagicMock, patch
from users.match import find_and_notify_matches


@patch("users.match.send_match_notification")
@patch("users.match.generate_match_data")
@patch("users.match.get_potential_matches")
def test_should_notify_user_when_item_is_lost(mock_get_matches, mock_generate_data, mock_notify):
    # Arrange
    mock_item = MagicMock()
    mock_item.status = "lost"
    mock_item.user.email = "user@example.com"
    mock_item.name = "Chave"

    mock_match = MagicMock()
    mock_get_matches.return_value = [mock_match]
    mock_generate_data.return_value = [{"name": "Chave encontrada"}]

    # Act
    find_and_notify_matches(mock_item)

    # Assert
    mock_item.matches.add.assert_called_once_with(mock_match)
    mock_item.save.assert_called_once()
    mock_generate_data.assert_called_once_with([mock_match])
    mock_notify.delay.assert_called_once_with(
        to_email="user@example.com",
        item_name="Chave",
        matches=[{"name": "Chave encontrada"}],
    )


@patch("users.match.send_match_notification")
@patch("users.match.generate_match_data")
@patch("users.match.get_potential_matches")
def test_should_notify_user_when_item_is_found(mock_get_matches, mock_generate_data, mock_notify):
    # Arrange
    found_item = MagicMock()
    found_item.status = "found"
    found_item.name = "Carteira"

    lost_item = MagicMock()
    lost_item.name = "Carteira perdida"
    lost_item.user.email = "lost@example.com"
    lost_item.matches.all.return_value = ["match1"]

    mock_get_matches.return_value = [lost_item]
    mock_generate_data.return_value = ["match1"]

    # Act
    find_and_notify_matches(found_item)

    # Assert
    lost_item.matches.add.assert_called_once_with(found_item)
    lost_item.save.assert_called_once()
    mock_generate_data.assert_called_once_with(["match1"])
    mock_notify.delay.assert_called_once_with(
        to_email="lost@example.com",
        item_name="Carteira perdida",
        matches=["match1"],
    )

@patch("users.match.send_match_notification")
@patch("users.match.get_potential_matches")
def test_should_not_notify_when_no_matches_found(mock_get_matches, mock_notify):
    # Arrange
    mock_item = MagicMock()
    mock_item.status = "lost"

    mock_get_matches.return_value = []

    # Act
    find_and_notify_matches(mock_item)

    # Assert
    mock_item.matches.add.assert_not_called()
    mock_item.save.assert_not_called()
    mock_notify.delay.assert_not_called()

'''
@patch("users.match.send_match_notification")
@patch("users.match.generate_match_data")
@patch("users.match.get_potential_matches")


def test_no_action_for_invalid_status(mock_get_matches, mock_generate_data, mock_notify):
    # Arrange
    mock_item = MagicMock()
    mock_item.status = "invalid"

    # Act
    find_and_notify_matches(mock_item)

    # Assert
    mock_get_matches.assert_not_called()
    mock_item.matches.add.assert_not_called()
    mock_item.save.assert_not_called()
    mock_generate_data.assert_not_called()
    mock_notify.delay.assert_not_called()
'''