from sentence_transformers import SentenceTransformer
import psycopg2

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
    config = load_config()
    conn = connect(config)
    cursor = conn.cursor()

    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

    embedded_message = input("What is the movie about?")
    embedding = model.encode(embedded_message)
    formattedEmbedding = str(embedding).replace('  ', ', ').replace(' -', ', -')

    #find closest 3 vector matches to the embedding of user query using cosine similarity
    sqlCode = "SELECT title, release_year FROM film ORDER BY embedding <=> '" + formattedEmbedding + "' LIMIT 3;"

    cursor.execute(sqlCode)
    data = cursor.fetchall()

    print("Here are the top 3 results:\n" + data[0][0] + " (" + str(data[0][1]) + ")\n" + data[1][0] + " (" + str(data[1][1]) + ")\n" + data[2][0] + " (" + str(data[2][1]) + ")\n")

    conn.close()

