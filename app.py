#all the modules
import speech_recognition as sr     #Voice recognizaion module 
import streamlit as st              #application des module
import os                           #interaction with OS
import sqlite3                      #DB
import google.generativeai as genai         #Google API module
import assemblyai as aai                    #assemlyai Module 

from dotenv import load_dotenv
load_dotenv()                    ## load all the environemnt variables

#connect api fectch from .env for ASSEMBLY AI
assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY") #test again 

#connect api fectch from .env for GOOGLE GENAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.header("App To Retrieve SQL Data") #app
# Apply the background image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
 background-image: url(https://img.freepik.com/free-vector/abstract-paper-style-background_52683-134881.jpg?size=626&ext=jpg);
 background-size: cover;
}
[data-testid="stHeader"] {
background-color: rgb(0, 0, 0 ,0);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

#assembly function to conversion of Hindi voice to TEXT
def transcribe_audio(audio_file_path):  #3
    try:
        config = aai.TranscriptionConfig(language_code="hi")
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file_path)
        return transcript.text
    except Exception as e:
        return f"Error: {e}"
    
# Record the voice and transcribe the audio call transcribe ausio
def record_and_transcribe_audio(file_path):  #2
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Recording...")
        audio = r.listen(source)
        
    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())
    
    st.write("Transcribing...")
    transcript_text = transcribe_audio(file_path)
    question=st.text_input("Input:", value=transcript_text,key="input") 
    submit=st.button("Ask the question")


## Define Your Prompt
prompt=[
    """
    you are a great vocublary expert in tranlsation detect the text of the text is in HINDI comvert the text into ENGLISH the move ahead if in english no need of doing anything 
    You are an expert in converting English questions to SQL queries!
The SQL database has the tables SALES and Products with the following columns:

For the SALES table:
- SaleID (INTEGER PRIMARY KEY)
- Date (DATE)
- CustomerID (INTEGER)
- EmployeeID (INTEGER)
- TotalAmount (NUMERIC(10, 2))

For the Products table:
- ProductID (INTEGER PRIMARY KEY)
- ProductName (VARCHAR(255))
- Description (TEXT)
- UnitPrice (NUMERIC(10, 2))
- QuantityInStock (INTEGER)

For example:
Example 1 - How many sales transactions were made in the last week?
The SQL command could resemble this:
SELECT COUNT(*) FROM SALES WHERE Date >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK);

Example 2 - Retrieve all products with a unit price greater than $100.
The corresponding SQL query might be:
SELECT * FROM Products WHERE UnitPrice > 100;
also the sql code should not have ``` in beginning or end and sql word in output


    """
]

## Fucntion To retrieve query from the database
def read_sql_query(sql,db):             
    conn=sqlite3.connect(db)            #connection with database   
    cur=conn.cursor()               
    cur.execute(sql)                    #run the prompt fetched given from API
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:                    #print all
        print(row)
    return rows

## Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')       #genrative ,odel gemini pro
    response=model.generate_content([prompt[0],question])       #rquesting response
    return response.text 
    
#main fucntion if button= TRUE
def main():
    audio_file_path = "recorded_audio.m4a"
    record_button = st.button("हिंदी")
    if record_button:
        record_and_transcribe_audio(audio_file_path)   #1
    else:
        question=st.text_input("Input:",key="input")  
        submit=st.button("Ask the question")
        if submit:
            response=get_gemini_response(question,prompt)
            print(response)
            response=read_sql_query(response,"storedb")
            st.subheader("The Response is")
            for row in response:
             print(row)
             st.header(row)
             
# submit_value=main()

if __name__ == "__main__":
    main()
