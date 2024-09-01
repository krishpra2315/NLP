from os.path import curdir
from sentence_transformers import SentenceTransformer, util
import psycopg2
from torch.nn.functional import embedding

from config import load_config

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == '__main__':
    data_length = 1000
    config = load_config()
    conn = connect(config)
    cursor = conn.cursor()

    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

    #populate the embedding column
    for i in range(1, data_length + 1):
        #build statement with title and description of each film
        cursor.execute("SELECT title, description FROM public.film WHERE film_id = " + str(i))
        data = cursor.fetchall()
        embedded_message = "The film named " + data[0][0] + " is about " + data[0][1]
        # embed and format the returned value with proper SQL vector formatting
        embedding = model.encode(embedded_message)
        formattedEmbedding = str(embedding).replace('  ', ', ').replace(' -', ', -')
        #build SQL request to populate the embedding
        sqlCode = "UPDATE film SET embedding = '" + formattedEmbedding + "' WHERE film_id = " + str(i) + ";"
        cursor.execute(sqlCode)

    conn.commit()
    conn.close()