# GemType
GemType is a Python script that uses the Google Gemini API to generate responses to user input and types them at the cursor location.

## Installation
1. Clone the repository:
```bash
$ git clone https://github.com/AlgoVoyager/gemtype.git
$ cd gemtype
```
2. Install dependencies:
```bash
$ python -m venv gtvenv
$ gtvenv\Scripts\activate
$ pip install -r requirements.txt
```
3. Set up your API key:
```bash
$ cp .env.example .env
$ notepad .env
$ GEMINI_API_KEY=your_api_key_here
```
Add your Gemini API key to the .env file.

## Usage
```bash
$ python gemtype.py
```
Press Ctrl+Alt+Space to trigger the hotkey.

## License
MIT License
