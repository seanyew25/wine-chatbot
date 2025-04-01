import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")



# Configure Gemini API
genai.configure(api_key=gemini_api_key)

chroma_client = chromadb.PersistentClient(path="wine_chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_collection(
    name="wines",
    embedding_function=sentence_transformer_ef
)


model = genai.GenerativeModel('gemini-2.0-flash')

def wine_rag_query(query: str, max_price: int = 100, acidity: str = "Medium Acidity", wine_type: str = "Red Wine", k_results: int = 3, tannin=None, taste_profile_evaluation=False):


    structured_filters = {
        "$and": [
            {"price": {"$lt": max_price}},  # Filter by price range
            {"acidity": acidity},  # Filter by acidity
            {"product_type": wine_type}  # Filter by wine type
        ]
    }

    
    # filter based on semantic search and structured filters
    data = collection.query(
        query_texts=[query],
        n_results=k_results,
        where=structured_filters  
    )
    
    context_strings = []


    for doc, meta in zip(data["documents"][0], data["metadatas"][0]):
        meta_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in meta.items()])
        formatted_entry = f"{doc}\n\n{meta_info}"  # Combine document and metadata
        context_strings.append(formatted_entry)

    final_context = "\n\n---\n\n".join(context_strings)  

    # print(final_context) 

    tannin_query = ""
    if tannin is not None:
        tannin_query = f"Also, I want a wine with {tannin} tannins."

    if taste_profile_evaluation:
        taste_profile_evaluation = f"Please evaluate my taste profile."

    prompt = f"""
    You are a wine expert assistant. Use the following wine information to answer the question.
    If you don't know the answer, say you don't know based on the provided information.
    Do talk a bit about the wine you are recommending to show how it fits the user's use case
    If user asks for a taste profile evaluation, evaluate all the other wines provided and give a taste profile evaluation of the user
    and what wines you think the user likes.


    # Context:
    {final_context}

    Question: 
    I want a wine below ${max_price} with {acidity} acidity and type {wine_type}. In addition,
    {query}. {tannin_query} {taste_profile_evaluation}

    Answer:
    """
    

    response = model.generate_content(prompt)
    returned_response = f"Gemini says :\n{response.text}"
    return response.text


def wine_rag_chat(query, chat_history):
    context_strings = []
    data = collection.query(
        query_texts=[query],
        n_results=3,
    )

    for doc, meta in zip(data["documents"][0], data["metadatas"][0]):
        meta_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in meta.items()])
        formatted_entry = f"{doc}\n\n{meta_info}"  # Combine document and metadata
        context_strings.append(formatted_entry)

    final_context = "\n\n---\n\n".join(context_strings)  
    prompt = f"""
    You are a wine expert sommelier. Use the following wine information to answer the question.
    If you don't know the answer, say you don't know based on the provided information.
    Refer to the chat history for additional context.
    If the user asks for a food pairing, talk in depth about how the wine adds to the food pairing
    Explain your recommendation in detail


    # Chat History:
    chat history: 
    {chat_history}


    # Context:
    {final_context}

    Question: 
    {query}

    Answer:
    """
    response = model.generate_content(prompt)
    return response.text



# query = "Recommend a full-bodied red wine under $50 from Italy"


print("What's your maximum price? ")
price = input("Enter the maximum price: ")
print("""
What type of wine are you looking for?
- White Wine
- Red Wine
- Sweet Wine
- Zero Alcohol Wine
- Champagne & Sparkling
- Rose
- Orange Wine
- Sake
    """)
wine_type = input("Enter the type of wine: ")

print("What flavours do you like?")
flavour = input("Enter the flavours you like: ")

print("What body style do you like? ")
body_style = input("Enter the body style you like: ")
print("What is the acidity level you like? High Acidity, Medium Acidity, or Low Acidity")
acidity = input("Enter the acidity level you like: ")
tannin = None
if wine_type == "Red Wine":
    print("What tannin level do you like? ")
    tannin = input("Enter the tannin level you like: ")

print("Would you like an evaluation of your taste profile based on this survey? (yes/no)")
input_evaluation = input("Enter your choice: ")
if input_evaluation.lower() == "yes":
    taste_profile_evaluation = True
else:
    taste_profile_evaluation = False

query = "Recommend a wine with " + flavour + " and body " + body_style

if wine_type == "Red Wine":
    query += " and tannin " + tannin



survey_response = wine_rag_query(query, max_price=(int(price)), acidity=acidity, wine_type=wine_type, tannin=tannin, taste_profile_evaluation=taste_profile_evaluation)
print(survey_response)

# After the user completes the survey, ask if they want to continue with a normal chat
print("\nWould you like to ask a wine-related question? (yes/no)")
user_choice = input("Enter your choice: ")
chat_history = []
chat_history.append({"role": "user", "content": query})
chat_history.append({"role": "model", "content": survey_response})
if user_choice.lower() == "yes":
    print("Feel free to ask your wine-related question!")
    while True:
        user_query = input("Ask me anything about wines: ")
        if user_query.lower() == "exit":
            print("Goodbye! Feel free to ask me questions anytime.")
            break
        else:
            # Transition to chat mode
            chat_history_str = str(chat_history)
            response = wine_rag_chat(user_query, chat_history_str)
            chat_history.append({"role": "model", "content": response})
            chat_history.append({"role": "user", "content": user_query})
            print(response)
else:
    print("Thanks for completing the survey! Enjoy your wine selection.")
