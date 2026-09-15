# Flashcard Agent

An AI-powered CLI tool that transforms study notes, articles, and reading materials into structured question-and-answer flashcards using **Ollama** and **LangChain**.

---

## Features

- **Automated Key Takeaways**: Extracts core concepts and essential definitions from unstructured text.
- **Structured Output**: Guarantees clean front/back card pairs using Pydantic schema validation.
- **Powered by Gemini**: Utilizes `mistral` for fast, high-quality card generation.
- **Lightweight CLI**: Simple, no-fuss command-line interface.

---

## Prerequisites

- **Python 3.10+**
- Ollama `mistral` local model runtime installed and configured. See [Ollama Docs](https://ollama.com/docs) for setup instructions.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/henrikhaa14/flashcard-agent.git
cd flashcard-agent
```

### 2. Install Dependencies

```bash
pip install langchain langchain-ollama pydantic genanki
```

---

## Usage

1. Save your study text or notes in a text file (e.g., in the `resources/` folder).
2. Run the application:

```bash
python main.py
```

3. Enter the path to your text file when prompted:

```text
Enter the path to the input file: resources/sample.txt

Input data loaded successfully.

Front: What is the primary function of mitochondria?
Back: Mitochondria generate most of the cell's supply of ATP, used as a source of chemical energy.

Front: What process converts light energy into chemical energy in plants?
Back: Photosynthesis.
```

---

## Project Structure

```text
flashcard-generator/
├── resources/        # Directory for input text files (gitignored)
├── .env              # API keys and environment configuration (gitignored)
├── LICENSE           # MIT License
├── main.py           # Application entry point, model setup, and generation logic
└── README.md         # Project documentation
```

---

## Customization

You can customize generation behavior directly in `main.py`:

- **Card Count**: Update `"Create 8 flashcards..."` in the user message to generate more or fewer cards.
- **Model**: Change the model identifier in `ChatOllama()` (e.g., to another Ollama model).
- **System Instructions**: Adjust `system_prompt` in `create_agent()` to tailor card style, tone, or depth.

---

## License

This project is licensed under the [MIT License](LICENSE).
