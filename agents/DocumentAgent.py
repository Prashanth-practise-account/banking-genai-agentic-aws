from llm.LLMConnection import LLMConnection
from pypdf import PdfReader
from SystemPrompt import DocumentExtractionPrompt
import re
import json


def clean_json(response):
    cleaned_response = re.sub(r"```json\s*|```\s*", "", response).strip()
    return json.loads(cleaned_response)

class DocumentAgent:

    def document_parsing(self, document):
        self.text = ""
        file = PdfReader(document)

        for page in file.pages:
            self.text += (page.extract_text() or "") + "\n"
    
        return self.text
    
    def structured_document(self, document_text):

        prompt = DocumentExtractionPrompt.replace(
            "{document_text}", document_text
        )

        llm = LLMConnection()
        llm.connect()

        response = llm.generate_response(prompt=prompt)

        if hasattr(response, "content"):
            response = response.content

        clean_structure = clean_json(response)

        if not clean_structure:
            raise ValueError("LLM returned an empty response.")

        try:
            structure_data = clean_structure
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM did not return valid JSON: {clean_structure}"
            ) from e

        return structure_data
