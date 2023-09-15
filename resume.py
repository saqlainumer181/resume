import openai
import re
import logging
import json
import tiktoken
import PyPDF2
from flask import Flask, jsonify, request
import docx
import docx2txt

  



openai.api_key = "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"
openai.organization = "org-Ce9qI51pELKTrpTTstDGztbR"


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens



class ResumeParser():
    def __init__(self):
        
    
        # GPT-3 completion questions
        self.prompt_questions = \
        """Summarize the text below into a JSON with exactly the following structure {basic_info: {first_name, last_name, full_name, email, phone_number, location, portfolio_website_url, linkedin_url, github_main_page_url, university, education_level (BS, MS, or PhD), graduation_year, graduation_month, majors, GPA}, work_experience: [{job_title, company, location, duration, job_summary}], project_experience:[{project_name, project_description}]}
        """
            # set up this parser's logger
        logging.basicConfig(filename='logs/parser.log', level=logging.DEBUG)
        self.logger = logging.getLogger()

    def pdf2string(self: object, pdf_path: str) -> str:
        """
        Extract the content of a pdf file to string.
        :param pdf_path: Path to the PDF file.
        :return: PDF content string.
        """
        
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        pdf = ""
        for page in pdf_reader.pages:
            pdf += page.extract_text()
        
        pdf_str = "\n\n".join(pdf)
        pdf_str = re.sub('\s[,.]', ',', pdf_str)
        pdf_str = re.sub('[\n]+', '\n', pdf_str)
        pdf_str = re.sub('[\s]+', ' ', pdf_str)
        pdf_str = re.sub('http[s]?(://)?', '', pdf_str)
        return pdf_str
    

    
    def docx2string(self: object, docx_path: str) -> str:
        """
        Extract the content of a .docx file to a string.
        :param docx_path: Path to the .docx file.
        :return: .docx content string.
        """

        doc_str = docx2txt.process(docx_path)

      

        doc_str = "\n\n".join(doc_str)
        doc_str = re.sub('\s[,.]', ',', doc_str)
        doc_str = re.sub('[\n]+', '\n', doc_str)
        doc_str = re.sub('[\s]+', ' ', doc_str)
        doc_str = re.sub('http[s]?(://)?', '', doc_str)

        return doc_str


    def query_completion(self: object,
                        prompt: str,
                        engine: str = 'text-curie-001',
                        temperature: float = 0.0,
                        max_tokens: int = 100,
                        top_p: int = 1,
                        frequency_penalty: int = 0,
                        presence_penalty: int = 0) -> object:
        """
        Base function for querying GPT-3. 
        Send a request to GPT-3 with the passed-in function parameters and return the response object.
        :param prompt: GPT-3 completion prompt.
        :param engine: The engine, or model, to generate completion.
        :param temperature: Controls the randomnesss. Lower means more deterministic.
        :param max_tokens: Maximum number of tokens to be used for prompt and completion combined.
        :param top_p: Controls diversity via nucleus sampling.
        :param frequency_penalty: How much to penalize new tokens based on their existence in text so far.
        :param presence_penalty: How much to penalize new tokens based on whether they appear in text so far.
        :return: GPT-3 response object
        """
      

        estimated_prompt_tokens = num_tokens_from_string(prompt, engine)
        estimated_answer_tokens = (max_tokens - estimated_prompt_tokens)
        self.logger.info(f'Tokens: {estimated_prompt_tokens} + {estimated_answer_tokens} = {max_tokens}')

        response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=estimated_answer_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
        )
        return response
    
    def query_resume(self: object, pdf_str: str) -> dict:
        """
        Query GPT-3 for the work experience and / or basic information from the resume at the PDF file path.
        :param pdf_path: Path to the PDF file.
        :return dictionary of resume with keys (basic_info, work_experience).
        """
        resume = {}
        # pdf_str = self.pdf2string(pdf_path)
        prompt = self.prompt_questions + '\n' + pdf_str

        # Reference: https://platform.openai.com/docs/models/gpt-3-5
        engine = 'text-davinci-002'
        max_tokens = 4097

        response = self.query_completion(prompt,engine=engine,max_tokens=max_tokens)
        response_text = response['choices'][0]['text'].strip()
        resume = json.loads(response_text)
        return resume
    


ResumeParser_obj = ResumeParser()


# creating a Flask app
app = Flask(__name__)
  


@app.route('/parse_resume', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.pdf'):
        try:
            resume_str = ResumeParser_obj.pdf2string(file)
            json_resume = ResumeParser_obj.query_resume(resume_str)
          
            return jsonify({'information': json_resume})
        except Exception as e:
            return jsonify({'error': str(e)})
    elif file and file.filename.endswith('.docx'):
        try:
            resume_str = ResumeParser_obj.docx2string(file)
            json_resume = ResumeParser_obj.query_resume(resume_str)
          
            return jsonify({'information': json_resume})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'Invalid file format. Please upload a valid docx file'})




# curl -X POST -F "file=@path/to/your/pdf.pdf" http://localhost:5000/parse_resume



if __name__ == '__main__':
    app.run(debug=True)






