# wine-chatbot
Chatbot that uses RAG with Chroma DB to provide users wine recommendations from Wine Connection

## Setup Instructions

Follow these steps to set up the wine chatbot:

1. **Set up Virtual Environment:**
   - Make sure you have Python 3.12+ installed. 
   - Create a virtual environment by running:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Windows:** 
       ```bash
       venv\Scripts\activate
       ```
     - **MacOS/Linux:** 
       ```bash
       source venv/bin/activate
       ```

2. **Install Dependencies:**
   - Install the required libraries by running:
     ```bash
     pip install -r requirements.txt
     ```

3. **Create `.env` File:**
   - Create a `.env` file in the root directory of the project.

4. **Add API Key to `.env`:**
   - Add your `GEMINI_API_KEY` to the `.env` file like this:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

5. **Run the Chatbot:**
   - Once the setup is complete, run the following command to start the wine chatbot:
     ```bash
     python genAI.py
     ```


## Explanation of Files

### `setup.py`

This file is responsible for parsing the `wine_data_final.csv` and adding both metadata and wine data to the Chroma database. Here's how it works:

- **Metadata:** This includes structured data, such as:
  - `product_type` (e.g., red wine, white wine, etc.)
  - `price` (e.g., price range or specific price)
  - Other attributes you might filter by, depending on the wine's characteristics.

  Metadata allows users to filter the data based on structured attributes, making it easier to refine their search based on specific criteria.

- **Normal Data:** This includes unstructured data like:
  - Descriptions of the wines
  - Reviews, tasting notes, and other text-based information

  This data is used for similarity searches and to provide more nuanced responses in the chatbot.

### **Normal Chat Entrypoint**

For the normal chat functionality, the chatbot uses a **Retrieval-Augmented Generation (RAG)** pipeline. The steps involved are:

1. **User Query:** The chatbot receives a user query, which can be a question about wines or a request for recommendations.
   
2. **Similarity Search:** The RAG pipeline compares the user’s query to the **normal data** (unstructured text like descriptions) stored in the Chroma DB. Using a similarity search, it identifies relevant wines based on the textual content of the query.

3. **Return Results:** The pipeline then returns a set of relevant wines, based on similarity to the query, in response to the user’s request.

This allows the chatbot to provide recommendations or answer questions that are based on descriptive, unstructured wine data.

### **Quiz Entrypoint**

For the **quiz entrypoint**, the system combines both structured data (metadata) and unstructured data (normal data) to provide relevant wine recommendations based on user responses to a series of questions or filters. Here's the breakdown:

1. **User Input:** The user is prompted to answer a set of questions (e.g., preferred product type, budget, flavor profile).
   
2. **Structured Data (Metadata):** The quiz results are processed by filtering the wines based on structured data such as:
   - `product_type` (e.g., red, white, sparkling)
   - `price` (e.g., within a certain price range)
   - many more

3. **Unstructured Data (Normal Data):** In addition to the structured data, the chatbot also considers **unstructured data** such as descriptions and tasting notes to provide context for the wine recommendations. This allows the system to find wines that fit both the user's explicit preferences (like product type and price) as well as more subjective preferences (like flavor descriptions or wine characteristics).

4. **Return Results:** After filtering based on structured and unstructured data, the system returns a set of wines that are most relevant to the user’s inputs.

## Explanation of Files

### `setup.py`

This file is responsible for parsing the `wine_data_final.csv` and adding both metadata and wine data to the Chroma database. Here's how it works:

- **Metadata:** This includes structured data, such as:
  - `product_type` (e.g., red wine, white wine, etc.)
  - `price` (e.g., price range or specific price)
  - Other attributes you might filter by, depending on the wine's characteristics.

  Metadata allows users to filter the data based on structured attributes, making it easier to refine their search based on specific criteria.

- **Normal Data:** This includes unstructured data like:
  - Descriptions of the wines
  - Reviews, tasting notes, and other text-based information

  This data is used for similarity searches and to provide more nuanced responses in the chatbot.

### **Normal Chat Entrypoint**

For the normal chat functionality, the chatbot uses a **Retrieval-Augmented Generation (RAG)** pipeline. The steps involved are:

1. **User Query:** The chatbot receives a user query, which can be a question about wines or a request for recommendations.
   
2. **Similarity Search:** The RAG pipeline compares the user’s query to the **normal data** (unstructured text like descriptions) stored in the Chroma DB. Using a similarity search, it identifies relevant wines based on the textual content of the query.

3. **Return Results:** The pipeline then returns a set of relevant wines, based on similarity to the query, in response to the user’s request.

This allows the chatbot to provide recommendations or answer questions that are based on descriptive, unstructured wine data.

### **Quiz Entrypoint**

For the **quiz entrypoint**, the system combines both structured data (metadata) and unstructured data (normal data) to provide relevant wine recommendations based on user responses to a series of questions or filters. Here's the breakdown:

1. **User Input:** The user is prompted to answer a set of questions (e.g., preferred product type, budget, flavor profile).
   
2. **Structured Data (Metadata):** The quiz results are processed by filtering the wines based on structured data like:
   - `product_type` (e.g., red, white, sparkling)
   - `price` (e.g., within a certain price range)

3. **Unstructured Data (Normal Data):** In addition to the structured data, the chatbot also considers **unstructured data** such as descriptions and tasting notes to provide context for the wine recommendations. This allows the system to find wines that fit both the user's explicit preferences (like product type and price) as well as more subjective preferences (like flavor descriptions or wine characteristics).

4. **Return Results:** After filtering based on structured and unstructured data, the system returns a set of wines that are most relevant to the user’s inputs.

This approach ensures that the wine recommendations are not just based on predefined filters (like price or product type), but also on more nuanced characteristics that the user may prefer, leading to a more personalized experience. After the survey, the chatbot is also able to provide a description of the user's palate, and wines which align to it.



