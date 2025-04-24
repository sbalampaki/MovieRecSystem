import pandas as pd
from sqlalchemy import create_engine, text
import sys

try:
  
    engine = create_engine('mysql+pymysql://root:surgodriti@localhost/movieRecProject')
    
    with engine.connect() as connection:
     
        df = pd.read_csv('movies_updated.csv')
        df.to_sql('movies', con=engine, if_exists='replace', index=False)
        

except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1) 