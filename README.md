# wine-chatbot
Chatbot that uses RAG with Chroma DB to provide users wine recommendations from Wine Connection

## Setup Instructions

Follow these steps to set up the wine chatbot:

1. **Set up Virtual Environment:**
   - Make sure you have Python 3.8+ installed. 
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


