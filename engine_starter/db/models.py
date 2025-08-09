from sqlalchemy import Column, BigInteger, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'Asset'  # 注意大小写要和 C# 中一致

    Sid = Column(BigInteger, primary_key=True, autoincrement=True)  # 主键类型与C#一致
    Symbol = Column(String(20), unique=True, nullable=False)        # 股票代码
    AssetName = Column(String(100), nullable=True)                  # 公司名称，可选
    Exchange = Column(String(50), nullable=True)                    # 交易所，可选
    StartDate = Column(Date, nullable=False)                        # 开始日期，必填
    EndDate = Column(Date, nullable=False)                          # 结束日期，必填
    AutoCloseDate = Column(Date, nullable=True)                     # 可选
    FirstTraded = Column(Date, nullable=True)                       # 可选


    def __repr__(self):
        return f"<Asset(Symbol='{self.Symbol}', StartDate={self.StartDate})>"