import json
from unittest.mock import MagicMock, patch

from django.http import HttpResponseRedirect
from django.test import RequestFactory

from users.views import microsoft_callback


class TestMicrosoftCallbackMC_DC:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_CT1_missing_authorization_code(self):
        request = self.factory.get("/fake-url")
        request.session = {}

        response = microsoft_callback(request)

        assert response.status_code == 400
        content = json.loads(response.content)
        assert content["error"] == "Código de autorização não fornecido."

    @patch("users.views.login")  # Mock para evitar erro com MagicMock user
    @patch("users.views.RefreshToken.for_user")
    @patch("users.views.save_or_update_user")
    @patch("users.views.fetch_user_data")
    @patch("users.views.ConfidentialClientApplication.acquire_token_by_authorization_code")
    def test_CT2_token_valido(
        self,
        mock_acquire_token,
        mock_fetch_user_data,
        mock_save_or_update,
        mock_for_user,
        mock_login,
    ):
        mock_acquire_token.return_value = {"access_token": "valid_token"}
        mock_fetch_user_data.return_value = {"some": "data"}
        user_mock = MagicMock()
        mock_save_or_update.return_value = (user_mock, True)

        mock_refresh_token = MagicMock()
        mock_refresh_token.access_token = "mocked_access_token"
        mock_for_user.return_value = mock_refresh_token

        request = self.factory.get("/fake-url", {"code": "valid_code"})
        request.session = {}
        request.COOKIES = {}

        response = microsoft_callback(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        cookies = response.cookies
        assert "access_token" in cookies
        assert cookies["access_token"].value == "mocked_access_token"

    @patch("users.views.ConfidentialClientApplication.acquire_token_by_authorization_code")
    def test_CT3_token_response_sem_access_token(self, mock_acquire_token):
        mock_acquire_token.return_value = {"": "valid_token"}

        request = self.factory.get("/fake-url", {"code": "valid_code"})
        request.session = {}

        response = microsoft_callback(request)

        assert response.status_code == 400
        content = json.loads(response.content)
        assert content["error"] == "Falha ao adquirir token de acesso."

    @patch("users.views.ConfidentialClientApplication.acquire_token_by_authorization_code")
    def test_CT4_token_response_access_token_vazio(self, mock_acquire_token):
        mock_acquire_token.return_value = {"access_token": ""}

        request = self.factory.get("/fake-url", {"code": "valid_code"})
        request.session = {}

        response = microsoft_callback(request)

        assert response.status_code == 400
        content = json.loads(response.content)
        assert content["error"] == "Falha ao adquirir token de acesso."
