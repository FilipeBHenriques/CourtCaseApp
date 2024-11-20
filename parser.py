# parse.py

from bs4 import BeautifulSoup
import json
from bs4 import BeautifulSoup
import io
import re
import chardet



from bs4 import BeautifulSoup
import re



def replace_pattern(paragraph_text, pattern):
    # Find all matches of the pattern
    matches = list(re.finditer(pattern, paragraph_text))

    # We will go through the matches and modify the string accordingly
    modified_s = paragraph_text

    # Iterate over matches in reverse order to avoid messing up indices after modification
    for match in reversed(matches):
        start, end = match.span()

        # Insert \n before the match
        modified_s = modified_s[:start] + '\n' + modified_s[start:]

    return modified_s

def remove_commas_newlines(paragraph_text):
    # Remove newline before commas (e.g., "\n," becomes ",")
    paragraph_text = re.sub(r'\s*\n\s*,', ',', paragraph_text)
    # Remove newline after commas (e.g., ",\n" becomes ", ")
    paragraph_text = re.sub(r',\s*\n+', ', ', paragraph_text)
    return paragraph_text

# Function to remove extra spaces between words (normalize space to a single space)
def remove_extra_spaces(paragraph_text):
    # Replace multiple spaces with a single space
    paragraph_text = re.sub(r'\s+', ' ', paragraph_text)
    # Remove leading and trailing spaces
    paragraph_text = paragraph_text.strip()
    return paragraph_text

def remove_newlines_between_words(paragraph_text):
    # Replace newlines between words with a single space
    paragraph_text = re.sub(r'(?<=\S)\n(?=\S)', ' ', paragraph_text)
    return paragraph_text



def replace_pattern_art(paragraph_text):
    matches = list(re.finditer(r'\d+\.?°', paragraph_text))

    # We will go through the matches and modify the string accordingly
    modified_s = paragraph_text

    # Iterate over matches in reverse order to avoid messing up indices after modification
    for match in reversed(matches):
        start, end = match.span()

        # Capture the preceding text by slicing up to the match
        preceding_text = paragraph_text[:start].strip()  # Strip to remove trailing whitespace
        preceding_words = preceding_text.split()  # Split into words
        
        # Check if there are any preceding words
        if preceding_words:
            preceding_word = preceding_words[-1]  # Get the last word before the match
        else:
            preceding_word = ""  # No preceding word

        # Check if the preceding word is 'art.' or 'artigo'
        if preceding_word not in ['artigo', 'art.']:  # If it's not 'art.' or 'artigo'
            # Insert \n before the match
            modified_s = modified_s[:start] + '\n' + modified_s[start:]

    return modified_s


def clean_paragraph_text(paragraph_text):
    # Split the paragraph into lines and strip unnecessary whitespace
    lines = paragraph_text.split('\n')
    
    # Initialize an empty list to store the cleaned text
    cleaned_text = []
    
    # Regular expression to match patterns: a colon followed by '-', a number + ".", a letter + ")", or "I-" and "II-"
    #colon_pattern = re.compile(r':\s*[-\d\w\)]')
    number_dot_pattern = re.compile(r'\b\d+\.\s?(?![^\s])')
    letter_paren_pattern = re.compile(r'[a-zA-Z]\)\s')
    number_paren_pattern = re.compile(r'\d+\)\s')

    roman_pattern = re.compile(r'[IVXLCDM]+-')
    number_degree_pattern = re.compile(r'\d+\.?°')
    
    
    
    
    
    for i, line in enumerate(lines):

        
        if(number_degree_pattern.search(line)):
            line = replace_pattern_art(line)
        if(number_dot_pattern.search(line)):
            line = replace_pattern(line,number_dot_pattern)
        if (letter_paren_pattern.search(line)):
            line = replace_pattern(line,letter_paren_pattern)
        if(number_paren_pattern.search(line)):
            line = replace_pattern(line,number_paren_pattern)
        if (roman_pattern.search(line)):
            line = replace_pattern(line,roman_pattern)
        line = remove_commas_newlines(line)
        #line = remove_extra_spaces(line)
        line = remove_newlines_between_words(line)
        cleaned_text.append(line)
    final_text = ' '.join(cleaned_text)
        

    return final_text

def parse_html(file_storage):
    try:
        # Try decoding the file content as UTF-8
        html_content = file_storage.read().decode('utf-8')
        
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, fallback to ISO-8859-1 (Latin-1)
        file_storage.seek(0)
        html_content = file_storage.read().decode('ISO-8859-1')

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Helper function to extract values and properly format paragraphs with newlines
    def extract_value(label):
        # Fetch soup from the global context if not passed
        label_pattern = re.compile(r'.*' + re.escape(label) + r'.*', re.IGNORECASE)  # Case-insensitive regex
        rows = soup.find_all('td', text=label_pattern)  # Find all td elements that contain the label using regex

        if rows:
            text = []
            for row in rows:
                
                next_td = row.find_next('td')  # Get the next td in the row
                if next_td:
                    # If the label is "Decisão Texto Integral:"
                    if label == "Decisão Texto Integral:":
                        paragraph_text = next_td.get_text(separator='\n', strip=True)
                        if paragraph_text:  # Only add non-empty text
                            # Join the paragraphs with newlines to separate them
                            return clean_paragraph_text(paragraph_text)
                            

                    else:
                        # For other labels, just extract the text and append
                        text.append(next_td.get_text(separator='\n', strip=True))

            # Join all text parts with a single newline separating them (if multiple rows)
            return "\n".join(text).strip()  # Return the cleaned text

        return ''  # Return empty string if not found
    

    # Function to extract the tribunal from the title (assuming it's after "Acórdão do")
    def extract_tribunal(soup):
        # Attempt to find the tribunal in the <title> or <h1> tags
        title_tag = soup.find('title')  # Look for <title> tag
        if title_tag:
            # Use regex to find the tribunal after "Acórdão do"
            tribunal_pattern = re.compile(r'Acórdão do\s*(.*)', re.IGNORECASE)
            match = tribunal_pattern.search(title_tag.get_text())
            if match:
                return match.group(1).strip()

        h1_tag = soup.find('h1')  # Alternatively, look for an <h1> tag
        if h1_tag:
            # Use regex to find tribunal after "Acórdão do" in the h1 tag
            match = tribunal_pattern.search(h1_tag.get_text())
            if match:
                return match.group(1).strip()

        return ''  # Return empty string if not found
    
    
    # Extract metadata values
    processo = extract_value('Processo:')
    tribunal = extract_tribunal(soup)

    sumario = extract_value('Sumário :') or extract_value('Sumário:')
    descritores = extract_value('Descritores:')
    relator = extract_value('Relator:')
    decisao = extract_value('Decisão:')
    data = extract_value('Data do Acordão:')
    

    # Now, extract and clean the main body content (text within <p> tags)
    
    main_content = extract_value("Decisão Texto Integral:")
    

    # Return all extracted values, including the cleaned main content
    return processo, tribunal, sumario, descritores, relator, decisao, data, main_content





def fix_encoding_issues(text):
    """
    Fix encoding issues caused by double encoding or wrong decoding.
    """
    # Encode the text as bytes in Latin-1 (mimicking the original incorrect decoding)
    byte_representation = text.encode('latin1', errors='ignore')  # or 'replace' if you want to keep track of errors
    # Decode back to UTF-8
    fixed_text = byte_representation.decode('utf-8', errors='ignore')  # Convert back to proper UTF-8

    return fixed_text


def parse_json(json_file):
    try:
        # Load JSON data into a Python object (it could be a dictionary or a list)
        data = json.load(json_file)
        entries = []

        # Check if the data has the "entities" key (first format)
        if isinstance(data, dict) and 'entities' in data:
            data = data['entities']  # Extract the list from the "entities" key

        # Now we can assume the data is a list (from either format)
        if isinstance(data, list):
            for item in data:
                # Ensure that each item is a dictionary and contains the required keys
                if isinstance(item, dict) and 'name' in item and 'label' in item and 'url' in item:
                    # Encode/decode each string as UTF-8
                    
                    name = fix_encoding_issues(item['name'])
                    label =fix_encoding_issues(item['label'])
                    url = fix_encoding_issues(item['url'])
                    entries.append((name, label, url))
                else:
                    print(f"Skipping invalid entry: {item}")
        else:
            print(f"Unexpected data format: {data}")

        return entries

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error while processing JSON: {e}")
        return []



