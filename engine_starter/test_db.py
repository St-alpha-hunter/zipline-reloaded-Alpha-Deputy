# 新建 test_db.py
from engine_starter.db.db_utils import Session
from engine_starter.db.models import Asset

session = Session()
assets = session.query(Asset).all()
print("Asset 表字段：", Asset.__table__.columns.keys())
print("表数据数量：", len(assets))
session.close()