from typing import Tuple
from unittest.mock import Mock

import pytest
import questionary
from pytest_mock import MockerFixture

from offers_sdk_applifting.client import OffersClient
from offers_sdk_applifting.exceptions import ValidationError
from questionary_cli.actions import Actions
from questionary_cli.app import run_cli, run_is_finished


@pytest.fixture
def offers_client_mock(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=OffersClient)


def mock_questionary_select(
    mocker: MockerFixture, action: str
) -> Tuple[Mock, Mock]:
    action_mock = Mock()
    action_mock.ask.return_value = action
    selection_mock = mocker.patch.object(
        questionary,
        "select",
        return_value=action_mock,
    )
    return action_mock, selection_mock


class TestRunIsFinished:
    def test_run_is_finished_with_exit_action(
        self, mocker: MockerFixture, offers_client_mock: Mock
    ) -> None:
        # Arrange
        mock_questionary_select(mocker, Actions.EXIT)
        mock_print = mocker.patch.object(questionary, "print")

        # Act
        result = run_is_finished(offers_client_mock)

        # Assert
        assert result is True
        mock_print.assert_called_once_with("Bye!")

    @pytest.mark.parametrize(
        "action,command_object",
        [
            (
                Actions.REGISTER_PRODUCT,
                "questionary_cli.app.register_product",
            ),
            (
                Actions.GET_OFFERS,
                "questionary_cli.app.get_offers",
            ),
        ],
    )
    def test_run_is_unfinished_for_commands(
        self,
        mocker: MockerFixture,
        offers_client_mock: Mock,
        action: str,
        command_object: str,
    ) -> None:
        # Arrange
        mock_questionary_select(mocker, action)
        mock_command = mocker.patch(command_object)

        # Act
        is_finished = run_is_finished(offers_client_mock)

        # Assert
        assert is_finished is False
        mock_command.assert_called_once()


class TestRunCli:
    def test_run_cli_exits_on_exit_action(
        self, mocker: MockerFixture, offers_client_mock: Mock
    ) -> None:
        # Arrange
        mock_questionary_select(mocker, Actions.EXIT)
        mock_run_is_finished = mocker.patch(
            "questionary_cli.app.run_is_finished", side_effect=[True]
        )

        # Act
        run_cli(offers_client_mock)

        # Assert
        mock_run_is_finished.assert_called_once_with(
            offers_client_mock
        )

    def test_run_cli_continues_on_action_other_than_exit(
        self, mocker: MockerFixture, offers_client_mock: Mock
    ) -> None:
        """Test that run_cli continues looping until EXIT is selected."""
        # Arrange
        mock_questionary_select = Mock()
        mock_questionary_select.ask.side_effect = [
            Actions.REGISTER_PRODUCT,
            Actions.EXIT,
        ]
        mocker.patch.object(
            questionary,
            "select",
            return_value=mock_questionary_select,
        )
        mocker.patch.object(questionary, "print")
        mock_run_is_finished = mocker.patch(
            "questionary_cli.app.run_is_finished",
            side_effect=[False, True],
        )

        # Act
        run_cli(offers_client_mock)

        # Assert
        assert mock_run_is_finished.call_count == 2

    def test_run_cli_handles_exceptions_gracefully(
        self, mocker: MockerFixture, offers_client_mock: Mock
    ) -> None:
        """Test that run_cli catches and logs exceptions."""
        # Arrange
        mock_questionary_select = Mock()
        mock_questionary_select.ask.return_value = (
            Actions.REGISTER_PRODUCT
        )
        mocker.patch.object(
            questionary,
            "select",
            return_value=mock_questionary_select,
        )
        mock_print = mocker.patch.object(questionary, "print")
        error_message = "Product already exists"
        mocker.patch(
            "questionary_cli.app.run_is_finished",
            side_effect=[ValidationError(error_message), True],
        )

        # Act
        run_cli(offers_client_mock)

        # Assert
        mock_print.assert_called()
        # Check that the error message was printed
        call_args = mock_print.call_args
        assert (
            f"❌ An error occurred: {error_message}"
            in call_args[0][0]
        )
