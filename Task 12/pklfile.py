import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import faiss

# 1. Load the new dataset
df = pd.read_csv("D:\\PAI TASKS\\Task 12\\lecture_chunks.csv")

# Identify the column containing your QnA or lecture text
text_column = 'text' # Apne CSV ke mutabiq isay change karein

# 2. Preprocess your dataset[cite: 1]
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # remove punctuations[cite: 1]
    text = re.sub(r'\s+', ' ', text)           # removes extra space[cite: 1]
    return text

df['Cleaned_Text'] = df[text_column].apply(clean_text)

# 3. Embed questions/answers using Hugging Face MiniLM[cite: 1]
print("Loading model and generating embeddings...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') #[cite: 1]
embeddings = model.encode(df['Cleaned_Text'].values) #[cite: 1]
embeddings = np.array(embeddings)

# 4. Store vectors using FAISS[cite: 1]
print("Creating FAISS index...")
dimensions = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimensions) # Euclidean Distance[cite: 1]
faiss_index.add(embeddings) #[cite: 1]

# Save the index and dataframe for the Flask app
faiss.write_index(faiss_index, "lecture_faiss_index.index") #[cite: 1]
df.to_pickle("lecture_data.pkl") # Pickle format app mein load karne ke liye fast hai
print("Processing complete! Index and data saved.")