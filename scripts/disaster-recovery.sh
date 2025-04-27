#!/bin/bash
# Full system recovery procedure

# 1. Restore PostgreSQL
echo "Restoring PostgreSQL..."
PGPASSWORD=$DB_PASSWORD pg_restore -U $DB_USER -h $DB_HOST -d $DB_NAME \
  -F c --clean --if-exists \
  /backups/db/weekly/latest_full.dump

# 2. Rebuild Redis cache
echo "Rebuilding Redis cache..."
python << EOF
import redis
from app.models import Trade
r = redis.Redis(host='redis')
for trade in Trade.query.all():
    r.hset(f'trade:{trade.id}', mapping=trade.to_dict())
EOF

# 3. Verify consistency
echo "Running consistency checks..."
python verify-backups.py --full-check