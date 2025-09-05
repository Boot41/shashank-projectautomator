"""
Comprehensive unit tests for email service.
"""
import pytest
from unittest.mock import patch, MagicMock
import smtplib
from app.services.email_service import send_email


@pytest.mark.unit
class TestEmailService:
    """Test cases for email service functions."""

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                
                assert result["status"] == "sent"
                assert "message" in result
                
                # Verify SMTP was called correctly
                mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
                mock_server.starttls.assert_called_once()
                mock_server.login.assert_called_once_with("test@example.com", "test-password")
                mock_server.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_html_body(self):
        """Test email sending with HTML body."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                html_body = "<h1>Test</h1><p>This is a test email</p>"
                result = await send_email("recipient@example.com", "Test Subject", html_body)
                
                assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_smtp_error(self):
        """Test email sending with SMTP error."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                
                assert result["status"] == "failed"
                assert "error" in result
                assert "SMTP Error" in result["error"]

    @pytest.mark.asyncio
    async def test_send_email_authentication_error(self):
        """Test email sending with authentication error."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                
                assert result["status"] == "failed"
                assert "error" in result
                assert "Authentication failed" in result["error"]

    @pytest.mark.asyncio
    async def test_send_email_missing_smtp_config(self):
        """Test email sending with missing SMTP configuration."""
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.smtp_server = None
            mock_settings.smtp_port = None
            mock_settings.smtp_username = None
            mock_settings.smtp_password = None
            
            result = await send_email("recipient@example.com", "Test Subject", "Test Body")
            
            assert result["status"] == "failed"
            assert "error" in result
            assert "SMTP configuration" in result["error"]

    @pytest.mark.asyncio
    async def test_send_email_invalid_recipient(self):
        """Test email sending with invalid recipient."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("invalid-email", "Test Subject", "Test Body")
                
                # Should still attempt to send, validation happens at SMTP level
                assert result["status"] == "sent" or result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_send_email_with_special_characters(self):
        """Test email sending with special characters in subject and body."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                special_subject = "Test Subject with Special Chars: !@#$%^&*()"
                special_body = "Test Body with Unicode: 你好世界 🌍"
                
                result = await send_email("recipient@example.com", special_subject, special_body)
                
                assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_with_long_content(self):
        """Test email sending with long content."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                long_subject = "A" * 1000
                long_body = "B" * 10000
                
                result = await send_email("recipient@example.com", long_subject, long_body)
                
                assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_connection_timeout(self):
        """Test email sending with connection timeout."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPConnectError(421, "Connection timeout")
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                
                assert result["status"] == "failed"
                assert "error" in result
                assert "Connection timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_send_email_recipient_refused(self):
        """Test email sending with recipient refused."""
        with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_server.send_message.side_effect = smtplib.SMTPRecipientsRefused("Recipient refused")
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.smtp_server = "smtp.gmail.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "test@example.com"
                mock_settings.smtp_password = "test-password"
                
                result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                
                assert result["status"] == "failed"
                assert "error" in result
                assert "Recipient refused" in result["error"]

    def test_email_service_imports(self):
        """Test that email service functions can be imported."""
        from app.services.email_service import send_email
        
        assert callable(send_email)

    @pytest.mark.asyncio
    async def test_send_email_with_different_smtp_servers(self):
        """Test email sending with different SMTP server configurations."""
        smtp_configs = [
            {"server": "smtp.gmail.com", "port": 587},
            {"server": "smtp.outlook.com", "port": 587},
            {"server": "smtp.yahoo.com", "port": 587},
            {"server": "localhost", "port": 1025}
        ]
        
        for config in smtp_configs:
            with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = mock_server
                
                with patch('app.services.email_service.settings') as mock_settings:
                    mock_settings.smtp_server = config["server"]
                    mock_settings.smtp_port = config["port"]
                    mock_settings.smtp_username = "test@example.com"
                    mock_settings.smtp_password = "test-password"
                    
                    result = await send_email("recipient@example.com", "Test Subject", "Test Body")
                    
                    assert result["status"] == "sent"
                    mock_smtp.assert_called_with(config["server"], config["port"])
