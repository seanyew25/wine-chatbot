import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# Load the CSV data
df = pd.read_csv("wine_data_final.csv", sep=";")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="wine_chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
collection = chroma_client.create_collection(name="wines", embedding_function=sentence_transformer_ef)

# Prepare documents and metadata
documents = []
metadatas = []
ids = []

for idx, row in df.iterrows():
    # Create document text
    full_document_text = "\n".join([
        f"Name: {row['name']}",
        f"Description: {row['description']}",
        f"Grape Varietal: {', '.join(row['grape_varietal']) if isinstance(row['grape_varietal'], list) else row['grape_varietal']}",
        f"Producer: {row['producer'] or 'N/A'}",
        f"Region: {row['region'] or 'N/A'}",
        f"Country: {row['country'] or 'N/A'}",
        f"mouth_attribute: {row['mouth_attribute'] or 'N/A'}",
        f"nose_attribute: {row['nose_attribute'] or 'N/A'}",
        f"legumes_pairing: {row['legumes_pairing'] or 'N/A'}",
        f"meat_pairing: {row['meat_pairing'] or 'N/A'}",
        f"fermentation_maceration: {row['fermentation_&_maceration'] or 'N/A'}",
        f"seafood_pairing: {row['seafood_pairing'] or 'N/A'}",
        f"acidity: {row['acidity'] or 'N/A'}",
        f"aging: {row['aging'] or 'N/A'}",
        f"product_type: {row['product_type'] or 'N/A'}",
        f"winemakers: {row['winemakers'] or 'N/A'}",

    ])


    metadata_dict = {
        "acidity": row.get("acidity", "N/A"),
        "aging": row.get("aging", "N/A"),
        "alcohol": row.get("alcohol", "N/A"),
        # "body": row.get("body", "N/A"),
        "density": row.get("density", "N/A"),
        "harvest_method": row.get("harvest_method", "N/A"),
        "price": row.get("price", "N/A"),
        "product_type": row.get("product_type", "N/A"),
        "sku": row.get("sku", "N/A"),
        "vintage": row.get("vintage", "N/A"),
        "volume(ml)": row.get("volume(ml)", "N/A"),
        "winemakers": row.get("winemakers", "N/A"),
    }


    
    # Create metadata dictionary
    # metadata = {col: row[col] for col in df.columns 
    #             if col not in ['name', 'description', 'grape_varietal', 
    #                           'producer', 'region', 'country'] 
    #             and not pd.isna(row[col])}
    documents.append(full_document_text)
    metadatas.append(metadata_dict)
    
    # Create ID
    ids.append(str(idx))

# Add to ChromaDB
collection.add(
    documents=documents,
    ids=ids,
    metadatas=metadatas,
)

print(f"Added {len(ids)} wine records to ChromaDB")