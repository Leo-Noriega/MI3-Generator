# JSON Extractor Script

This scripts gather the info of our devices in our database, and then retrieves the info of those devices in the SISMEDIA API. 
Stores the info in individual json and then combines all of those in easy jsons for the insert of data in our database.

## Requirements

- Python 3.x
- `venv` for virtual environments

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
      ```sh
      venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```sh
      source venv/bin/activate
      ```

4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

5. Run the scripts as needed, for example:
    ```sh
    python Main.py
    ```