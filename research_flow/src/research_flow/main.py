#!/usr/bin/env python
import os
from datetime import datetime

from langtrace_python_sdk import langtrace

from crewai.flow import Flow, listen, start
from .crews.research_crew.src.research_crew.crew import ResearchCrew
from .crews.define_crew.src.define_crew.crew import DefineCrew
from .config import RESEARCH_FLOW_INPUT_VARIABLES

api_key = os.getenv('LANGTRACE_API_KEY')
langtrace.init(api_key=api_key)

class ResearchFlow(Flow):
    input_variables = RESEARCH_FLOW_INPUT_VARIABLES
    
    def print_content_to_file(self, final_content):
        print("Saving research")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            # Convert each dictionary to a string representation
            content_strings = [str(item) for item in final_content]
            f.write("[\n  " + ",\n  ".join(content_strings) + "\n]")

    @start()
    def generate_research(self):
        print("Generating research")
        result = ResearchCrew().crew().kickoff(inputs=self.input_variables)
        print("research generated", result.raw)
        return result.pydantic

    @listen(generate_research)
    def generate_content(self, plan):
        final_content = []
        for section in plan.sections:
            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section.model_dump_json()            
            final_content.append(DefineCrew().crew().kickoff(inputs=writer_inputs).raw)
            #final_content.append(writer_inputs)
        print(final_content)
        return final_content
    
    @listen(generate_research)
    def save_to_markdown(self, content):
        output_folder = self.input_variables["output_folder"]
        os.makedirs(output_folder, exist_ok=True)
        
        topic = self.input_variables["topic"]
        audience_level = self.input_variables["audience_level"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{topic}_{audience_level}_{timestamp}.md".replace(" ", "_")
        
        output_path = os.path.join(output_folder, file_name)
        
        # Format content as markdown
        formatted_content = []
        for section in content:
            if isinstance(section, (str, dict)):
                formatted_content.append(str(section))
        
        markdown_content = "\n\n".join(formatted_content)
        
        print(f"Writing to file: {output_path}")
        print(f"Content length: {len(markdown_content)}")
        
        try:
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(markdown_content)
                f.flush()  # Force write to disk
                os.fsync(f.fileno())  # Ensure it's written to disk
            
            # Verify the file was written
            if os.path.exists(output_path):
                print(f"File successfully written: {output_path}")
                with open(output_path, 'r', encoding='utf-8') as f:
                    verification = f.read()
                print(f"Verified content length: {len(verification)}")
            else:
                print("Error: File was not created")
                
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            raise
            
        return {
            "file_path": output_path,
            "content": markdown_content
        }

def kickoff():
    research_flow = ResearchFlow()
    research_flow.kickoff()

def plot():
    research_flow = ResearchFlow()
    research_flow.plot()

if __name__ == "__main__":
    kickoff()