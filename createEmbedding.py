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

    for i in range(1, data_length + 1):
        cursor.execute("""
                          SELECT title, description FROM public.film
                          WHERE film_id = """ + str(i))
        data = cursor.fetchall()
        embedded_message = "The film named " + data[0][0] + " is about " + data[0][1]
        print(embedded_message)
        embedding = model.encode(embedded_message)
        formattedEmbedding = str(embedding).replace('  ', ', ').replace(' -', ', -')
        sqlCode = "UPDATE film SET embedding = '" + formattedEmbedding + "' WHERE film_id = " + str(i) + ";"
        cursor.execute(sqlCode)

    cursor.execute("""
                              SELECT embedding FROM public.film
                              WHERE film_id =1000
                  """)
    print(cursor.fetchall())

    conn.commit()
    conn.close()

    '''model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    query_embedding = model.encode('How big is London')
    passage_embedding = model.encode(['London has 9,787,426 inhabitants at the 2011 census',
                                      'London is known for its finacial district'])
    print("Similarity:", util.dot_score(query_embedding, passage_embedding))

    query_embedding2 = model.encode('How many kids do you havese')
    passage_embedding2 = model.encode(['I have 3 kids',
                                      'Barcelona is 3000 meters wide'])
    print("Similarity:", util.dot_score(query_embedding2, passage_embedding2))'''