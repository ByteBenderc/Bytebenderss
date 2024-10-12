import os
import PyPDF2
from docx import Document
import g4f
import gradio as gr

# Paths for different options
paths = {
    "AVAS": {
        "pdf": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Регламенты сертификации\AVAS\AVAS_EN.pdf',
        "directory": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Бизнес-требования к разработке\AVAS'
    },
    "Braking": {
        "pdf": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Регламенты сертификации\Braking\Braking_EN.pdf',
        "directory": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Бизнес-требования к разработке\Braking Systems'
    },
    "Wipers and Washers": {
        "pdf": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Регламенты сертификации\Wipe and wash\Wipe_and_wash_ENG.pdf',
        "directory": r'C:\Users\Nimtey\Desktop\Piter\Атом\Тренировочные данные (train)\Бизнес-требования к разработке\Wipers and Washers'
    }
}

# Function to extract text from a PDF file
def extract_pdf_text(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() or ''  # Use or '' to handle pages that return None
        return text

# Function to extract text from a DOCX file
def extract_docx_text(docx_file):
    doc = Document(docx_file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to process all PDFs and DOCXs in the directory and the specific PDF file
def process_files(option):
    specific_pdf = paths[option]['pdf']
    directory_path = paths[option]['directory']
    all_texts = ""

    # Extract text from the specific PDF
    print(f"Processing: {specific_pdf}")
    specific_text = extract_pdf_text(specific_pdf)
    all_texts += f"\n\n=== Content of {os.path.basename(specific_pdf)} ===\n{specific_text}"

    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if filename.endswith(".pdf"):
            print(f"Processing PDF: {file_path}")
            pdf_text = extract_pdf_text(file_path)
            all_texts += f"\n\n=== Content of {filename} ===\n{pdf_text}"
        elif filename.endswith(".docx"):
            print(f"Processing DOCX: {file_path}")
            docx_text = extract_docx_text(file_path)
            all_texts += f"\n\n=== Content of {filename} ===\n{docx_text}"
    
    return all_texts

# Function to analyze business requirements
def analyze_requirements(option, user_input):
    # Process the selected files (but we don't need to return the content)
    file_content = process_files(option)
    
    # Prepare GPT-4 prompt with user input
    prompt = user_input + "\nПожалуйста, проанализируйте бизнес-требования и напишите все ошибки, не переписывая текст в этом примере:"
    
    # Generate a response from GPT-4
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Adjust the model if needed
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Get the analysis result
    if isinstance(response, str):
        analysis_result = response
    else:
        analysis_result = response.get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
    
    # Check compliance based on analysis result
    compliance_result = "соответствует" if "нет ошибок" in analysis_result else "несоответствует"

    return analysis_result.strip(), compliance_result  # Return only the analysis result and compliance

# Create the Gradio interface
def create_interface():
    option_buttons = gr.Radio(
        choices=["AVAS", "Braking", "Wipers and Washers"],
        label="Выберите опцию",
        value="AVAS"  # Default value
    )
    
    user_input = gr.Textbox(
        lines=20, 
        placeholder='Введите ваши бизнес-требования здесь...'
    )

    output = gr.Textbox()  # For analysis errors
    compliance_output = gr.Textbox()  # For compliance result

    def run_analysis(option, user_input):
        analysis_result, compliance_result = analyze_requirements(option, user_input)
        return analysis_result, compliance_result  # Return both analysis and compliance

    # Gradio interface setup
    interface = gr.Interface(
        fn=run_analysis,
        inputs=[option_buttons, user_input],
        outputs=[output, compliance_output],  # Update outputs to include compliance
        title="Анализатор бизнес-требований",
        description="Выберите опцию и введите ваши бизнес-требования для анализа."
    )
    return interface

# Launch the Gradio app
if __name__ == "__main__":
    create_interface().launch()
