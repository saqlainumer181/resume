1. open a folder and clone the project

git clone https://gitlab.com/saqlainumer/ai-resume.git

2. Move to project directory, install the requirements.txt, open cmd terminal in the project directory

pip install -r requirements.txt

3. Run the following command in the terminal to execute the main function

python resume.py

4. open another terminal in the same directory and run the following command. resume.pdf and resume.docx are the test files. you can add your resume files and change file name in the following command

curl -X POST -F "file=resume.pdf" http://localhost:5000/parse_resume

5. you can also use postman, use the following link for POST command: http://localhost:5000/parse_resume (optional)
