try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
# gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_key = st.secrets["gemini"]["api_key"]

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="wine_chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_collection(
    name="wines",
    embedding_function=sentence_transformer_ef
)

model = genai.GenerativeModel('gemini-2.0-flash')
print('gemini model loaded')

def wine_rag_query(query: str, max_price: int = 100, acidity: str = "Medium Acidity", wine_type: str = "Red Wine", k_results: int = 5, tannin=None, taste_profile_evaluation=False):
    # filter based on structured data such as price, acidity, and wine type
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
    if len(data["documents"][0]) == 0:
        data = collection.query(
            query_texts=[query],
            n_results=k_results,
        )
    
    context_strings = []

    for doc, meta in zip(data["documents"][0], data["metadatas"][0]):
        meta_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in meta.items()])
        formatted_entry = f"{doc}\n\n{meta_info}"  # Combine document and metadata
        context_strings.append(formatted_entry)

    final_context = "\n\n---\n\n".join(context_strings)  

    tannin_query = ""
    if tannin is not None:
        tannin_query = f"Also, I want a wine with {tannin} tannins."

    if taste_profile_evaluation:
        taste_profile_evaluation = f"Please evaluate my taste profile."

    prompt = f"""
    You are a wine expert assistant. Use the following wine information to answer the question.
    If you don't know the answer, try to use your own knowledge base.
    Explain about the wine you are recommending to show how it fits the user's use case
    Evaluate all the other wines provided and give a taste profile evaluation of the user.
    After recommending the primary wine that fits the user's use case and giving the taste profile, provide a list of other wines that fit the user's taste profile.
    Explain why you are recommending the subsequent wines and how they fit the user's taste profile.
    For the taste profile part, format the response as **Taste Profile Evaluation:** and **Other Wines That Fit Your Taste Profile:**

    # Context:
    {final_context}

    Question: 
    I want a wine below ${max_price} with {acidity} acidity and type {wine_type}. In addition,
    {query}. {tannin_query} {taste_profile_evaluation}

    Answer:
    """
    
    response = model.generate_content(prompt)
    return response.text

def wine_rag_chat(query, chat_history):
    context_strings = []
    data = collection.query(
        query_texts=[query],
        n_results=5,
    )

    for doc, meta in zip(data["documents"][0], data["metadatas"][0]):
        meta_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in meta.items()])
        formatted_entry = f"{doc}\n\n{meta_info}"  # Combine document and metadata
        context_strings.append(formatted_entry)

    final_context = "\n\n---\n\n".join(context_strings)  
    prompt = f"""
    You are a wine expert sommelier. Use the following wine information to answer the question.
    If you don't know the answer, try to recommend something from your own knwowledge base.
    Explain about the wine you are recommending to show how it fits the user's use case. You are marketing the wine to the user.

    Refer to the chat history for additional context.

    # Chat History:
    {chat_history}

    # Context:
    {final_context}

    Question: 
    {query}

    Answer:
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit app
def main():
    st.title("🍷 Wine Recommendation Assistant")
    st.write("This is a POC for our recommendation system. The actual UI is laid out in our Figma")
    
    # Initialize session states
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "taste_profile" not in st.session_state:
        st.session_state.taste_profile = None

    # Survey section
    with st.expander("🧾 Wine Preference Survey", expanded=True):
        
        st.write("Let's find the perfect wine for you!")
        
        price = st.number_input("What's your maximum price?", min_value=10, max_value=1000, value=50)
        wine_type = st.selectbox(
            "What type of wine are you looking for?",
            ["White Wine", "Red Wine", "Sweet Wine", "Zero Alcohol Wine", 
             "Champagne & Sparkling", "Rose", "Orange Wine", "Sake"]
        )
        flavour = st.text_input("What flavors do you like? (e.g., fruity, oaky, citrus)")
        body_style = st.selectbox(
            "What body style do you prefer?",
            ["Light-bodied", "Medium-bodied", "Full-bodied"]
        )
        acidity = st.selectbox(
            "What acidity level do you prefer?",
            ["High Acidity", "Medium Acidity", "Low Acidity"]
        )
        tannin = None
        if wine_type == "Red Wine":
            tannin = st.select_slider(
                "What tannin level do you prefer?",
                ["Soft", "Velvetly", "Silky", "Medium", "Grippy", "Chewy", "Firm", "Abrasive"]
            )
        # taste_profile_evaluation = st.checkbox(
        #     "Would you like an evaluation of your taste profile based on this survey?"
        # )
        
        if st.button("Get Wine Recommendations"):
            query = f"Recommend a wine with {flavour} and body {body_style}"
            if wine_type == "Red Wine":
                query += f" and tannin {tannin}"
            
            with st.spinner("Finding the perfect wine for you..."):
                survey_response = wine_rag_query(
                    query, 
                    max_price=int(price), 
                    acidity=acidity, 
                    wine_type=wine_type, 
                    tannin=tannin, 
                    taste_profile_evaluation=True
                )
                
                # Extract and save taste profile
                if "**Taste Profile Evaluation:**" in survey_response:
                    parts = survey_response.split("**Taste Profile Evaluation:**")
                    recommendation_part = parts[0]
                    taste_profile_part = parts[1].strip()
                    profile_parts = taste_profile_part.split("**Other Wines That Fit Your Taste Profile:**")
                    st.session_state.taste_profile = profile_parts[0].strip()
                    display_response = f"{recommendation_part}\n\n**Taste Profile Evaluation:**\n{taste_profile_part}"
                else:
                    display_response = survey_response
                    st.session_state.taste_profile = None

                # Update chat history
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.session_state.chat_history.append({"role": "model", "content": display_response})
                
                st.markdown("## 🍾 Your Wine Recommendations")
                st.markdown(display_response)

    # Taste profile recommendations section
    if st.session_state.taste_profile:
        st.markdown("## 🎯 Recommendations Based on Your Taste Profile")
        st.write("Here are more recommendations tailored to your unique preferences:")
        st.markdown(f"**Your Taste Profile:**\n{st.session_state.taste_profile}")
        
        if st.button("Get Updated Recommendations Using My Taste Profile"):
            with st.spinner("Discovering new wines for your palate..."):
                profile_query = f"Based on this taste profile: {st.session_state.taste_profile}. Recommend wines that match these characteristics."
                
                profile_response = wine_rag_chat(
                    profile_query,
                    chat_history=''
                )
                
                st.session_state.chat_history.append({"role": "user", "content": profile_query})
                st.session_state.chat_history.append({"role": "model", "content": profile_response})
                
                st.markdown("### 🍷 Tailored Recommendations")
                st.markdown(profile_response)

    # Chat section
    st.markdown("## 💬 AI Wine Sommelier")
    st.write("Ask me anything about wines! I can provide you with recommendations, food pairings, and more.")
    
    user_query = st.text_input("Your wine question:", key="chat_input")
    
    if st.button("Ask", key="chat_button"):
        if user_query:
            with st.spinner("Thinking about your wine question..."):
                chat_history_str = str(st.session_state.chat_history)
                response = wine_rag_chat(user_query, chat_history_str)
                
                # Update chat history
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                st.session_state.chat_history.append({"role": "model", "content": response})
                
                # Keep chat history manageable
                if len(st.session_state.chat_history) > 6:
                    st.session_state.chat_history = st.session_state.chat_history[-6:]
                
                st.markdown("### Response")
                st.markdown(response)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Sommelier:** {message['content']}")
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("---")

if __name__ == "__main__":
    main()