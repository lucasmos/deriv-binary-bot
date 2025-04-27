import unittest
import requests
from psycopg2 import connect

class DisasterRecoveryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cls.api_url = os.getenv('API_URL')

    def test_database_integrity(self):
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM trades 
                WHERE executed_at > NOW() - INTERVAL '7 days'
            """)
            self.assertGreater(cur.fetchone()[0], 0, "No recent trades found")

    def test_api_connectivity(self):
        resp = requests.get(f"{self.api_url}/health", timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'healthy')

if __name__ == '__main__':
    unittest.main()