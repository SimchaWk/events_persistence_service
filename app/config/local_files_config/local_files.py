from pathlib import Path
from dotenv import load_dotenv

from app.utils.formatted_date_util import formatted_datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent

load_dotenv(PROJECT_ROOT / '.env')

EVENTS_GRAPH_NETWORKX = PROJECT_ROOT / 'data' / f'terror_graph.pickle'
EVENTS_GRAPH_NETWORKX_SECOND = PROJECT_ROOT / 'data' / f'terror_graph_{formatted_datetime()}.pickle'

if __name__ == '__main__':
    print(EVENTS_GRAPH_NETWORKX)
