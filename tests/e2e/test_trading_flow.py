import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.usefixtures("live_server", "driver")
class TestTradingFlow:
    def test_quick_trade(self, auth):
        """Test placing a quick trade"""
        # Log in
        auth.login()
        
        # Navigate to trading page
        self.driver.get(f"{self.live_server.url}/trading")
        
        # Fill in trade details
        self.driver.find_element(By.ID, "quickBuyBtn").click()
        
        # Wait for success notification
        notification = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success")))
        
        assert "Trade placed successfully" in notification.text

    def test_bot_trading(self, auth):
        """Test starting and stopping the trading bot"""
        # Log in
        auth.login()
        
        # Navigate to trading page
        self.driver.get(f"{self.live_server.url}/trading")
        
        # Switch to bot tab
        self.driver.find_element(By.ID, "bot-tab").click()
        
        # Start bot
        self.driver.find_element(By.ID, "startBotBtn").click()
        
        # Verify bot started
        stop_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "stopBotBtn")))
        assert stop_button.is_displayed()
        
        # Stop bot
        stop_button.click()
        
        # Verify bot stopped
        start_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "startBotBtn")))
        assert start_button.is_displayed()