from flask import Flask, render_template, request
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Server start hotay hi model aur data load karein
print("Booting up Lecture QnA Bot...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
faiss_index = faiss.read_index("D:\\PAI TASKS\\Task 12\\lecture_index.index")
df = pd.read_pickle("D:\\PAI TASKS\\Task 12\\lecture_data.pkl")
text_column = 'text' # Apna column name yahan bhi same rakhein

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            # Search and match using similarity[cite: 1]
            query_embedding = model.encode([query])
            distances, indices = faiss_index.search(query_embedding, 5) # Top 5 results nikalne ke liye[cite: 1]
            
            for i in range(len(indices[0])):
                idx = indices[0][i]
                dist = distances[0][i]
                
                # Retrieve the actual text from the dataframe
                matched_text = df.iloc[idx][text_column] 
                results.append({
                    "text": matched_text, 
                    "distance": round(float(dist), 4)
                })
                
    return render_template("index.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)