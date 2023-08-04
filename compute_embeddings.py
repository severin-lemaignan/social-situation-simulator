import pandas as pd
import numpy as np

from langchain.embeddings import OpenAIEmbeddings

embeddings_model = OpenAIEmbeddings()

df = pd.read_csv("situation_1.csv")

# print(df)

ts = ["t-%s" % t for t in np.arange(0, 3.001, 0.5)]

embeddings = {}

i = 0
for idx, row in df.iterrows():

    for t in ts:
        desc = row[t]
        if type(desc) == str and desc:
            if desc not in embeddings:
                print("[%s] Computing embedding of %s..." % (i, desc))
                embeddings[desc] = embeddings_model.embed_query(desc)
                i += 1

df_embeddings = pd.DataFrame.from_dict(embeddings, orient="index")
df_embeddings.to_csv("embeddings.csv")
print(df_embeddings)
