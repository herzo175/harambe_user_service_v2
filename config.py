import os

import dotenv

dotenv.load_dotenv()

HARAMBE_DATA_SERVICE_ENDPOINT="http://localhost:3000"
HARAMBE_IDENTITY_SERVICE_ENDPOINT="http://localhost:3001"
HARAMBE_TRADING_SERVICE_ENDPOINT="http://localhost:3002"
TRADE_IT_API_ENDPOINT="https://ems.qa.tradingticket.com/api/v2"
TRADE_IT_API_KEY=os.getenv("TRADE_IT_API_KEY")
