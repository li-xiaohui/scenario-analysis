import json
import re

def fix_json_file(input_path: str, output_path: str):
    """Fix JSON file by removing comments and fixing syntax issues."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove single-line comments
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    
    # Remove trailing commas before closing braces/brackets
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Fix any remaining syntax issues
    try:
        # Try to parse the JSON to validate it
        data = json.loads(content)
        
        # Write the cleaned JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully fixed JSON file. Output saved to {output_path}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON after cleaning: {e}")
        print("Please manually fix the remaining issues in the JSON file.")

if __name__ == "__main__":
    fix_json_file("data/knowledge_graph_v2.json", "data/knowledge_graph_v2_fixed.json") 