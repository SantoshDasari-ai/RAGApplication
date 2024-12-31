import os
import glob
import re
import pandas as pd
from tqdm import tqdm
from langchain.docstore.document import Document as LangchainDocument


# Add this mapping dictionary at the top of your file or in a configuration file
SOURCE_MAPPING = {
    "CXPA_CX_BOK": "CXPA CX Book of Knowledge",
    "CX_Finance": "Finance",
    "Building Diversity Equity and Inclusiveness into a Customer Experience Ecosystem": "Building Diversity Equity",
    "CX_Customer Service": "Customer Service",
    "CX_C-Suite": "C-Suite",
    "CX_Marketing": "Marketing",
    "CX_Sponsorship": "Sponsorship",
    "CX_Sales": "Sales",
    "CX and Data Owners": "Data Owners",
    "CX_IT": "IT",
    "SalesAccountMgmt&CS": "Sales, Account Management & Customer Success",
    "CXPA_Guide_To_Developing_CX_Job_Descriptions": "Guide to Developing CX Job Descriptions",
    "CX_Operations": "Operations"
}

# This function either loads an existing dataset or creates a new one from text files
def load_or_generate_dataset_from_textfiles(txt_directory: str, dataset_dir: str, dataset_csv_path: str, force_reprocess: bool = False) -> list:
    """
    This function checks if we already have a dataset. If we do, it loads it.
    If we don't, or if we want to make a new one, it creates a dataset from text files.
    """

    # Check if we already have a dataset and don't need to make a new one
    if os.path.exists(dataset_dir) and not force_reprocess:
        print("We found a dataset! Let's use it.")
        context_dataset = pd.read_csv(dataset_csv_path)
    else:
        print("We need to make a new dataset from our text files.")
        context_dataset = generate_dataset_from_textfiles(txt_directory, dataset_csv_path)

    print("The dataset is ready to use!")
    # Turn our dataset into a special format that our program can use
    return convert_to_langchain_documents(context_dataset)

# This function creates a new dataset by reading text files
def generate_dataset_from_textfiles(txt_directory: str, dataset_csv_path: str) -> pd.DataFrame:
    # Find all the text files in our folder
    txt_files = glob.glob(os.path.join(txt_directory, '*.txt'))
    data = []
    # This pattern helps us get information from the file names
    pattern = r"(?P<filename>.+?)__.*__(?P<start_page>\d+)_{1,2}(?P<end_page>\d+)(?:__)?\.txt"

    # Go through each text file one by one
    for txt_file in tqdm(txt_files, desc="Reading Text Files"):
        try:
            # Get the file name without the folder path
            base_name = os.path.basename(txt_file)
            # Try to get information from the file name
            match = re.match(pattern, base_name)
            filename_metadata = match.groupdict() if match else {}

            # Open and read the text file
            with open(txt_file, 'r', encoding='utf-8') as file:
                content = file.read()

            # Save information about this file in our list
            data.append({
                "text": content,
                "filename": txt_file,
                "start_page": filename_metadata.get("start_page"),
                "end_page": filename_metadata.get("end_page"),
                "page_numbers": f"{filename_metadata.get('start_page', '')}-{filename_metadata.get('end_page', '')}",
                "source": filename_metadata.get("filename")
            })
                
        except Exception as e:
            print(f"Oops! We had trouble with this file: {txt_file}. Here's what went wrong: {e}")

    # Turn our list of data into a table (DataFrame)
    dataset_df = pd.DataFrame(data)
    # Save our table as a CSV file so we can use it later
    dataset_df.to_csv(dataset_csv_path, index=False)
    return dataset_df

# This function changes our dataset into a format that works with our AI tools
def convert_to_langchain_documents(dataset_df: pd.DataFrame) -> list:
    return [
        LangchainDocument(
            page_content=doc["text"],
            metadata={
                "source": SOURCE_MAPPING.get(doc["source"], doc["source"]),  # Use mapping if available, otherwise use original
                "start_page": doc.get("start_page"),
                "end_page": doc.get("end_page"),
                "filename": doc.get("filename", "unknown"),
                "page_numbers": doc.get("page_numbers")
            }
        )
        for doc in dataset_df.to_dict(orient='records')
    ]
