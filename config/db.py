from sqlalchemy import create_engine, MetaData


engine = create_engine(
    "mysql+pymysql://root:root_password@localhost:3306/librarydb")  # librarybstest

conn = engine.connect()
meta = MetaData()
