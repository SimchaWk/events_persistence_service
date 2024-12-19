from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parent.parent.parent

load_dotenv(PROJECT_ROOT / '.env')

GLOBAL_TERRORISM_CSV = PROJECT_ROOT / 'data' / 'globalterrorismdb_0718dist.csv'
SECONDARY_TERROR_CSV = PROJECT_ROOT / 'data' / 'RAND_Database_of_Worldwide_Terrorism_Incidents.csv'
GLOBAL_TERRORISM_CSV_MINI = PROJECT_ROOT / 'data' / 'GLOBAL_TERRORISM_CSV.csv'
SECONDARY_TERROR_CSV_MINI = PROJECT_ROOT / 'data' / 'SECONDARY_TERROR_CSV.csv'

if __name__ == '__main__':
    print(GLOBAL_TERRORISM_CSV)
