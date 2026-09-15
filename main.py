import random
from typing import Literal, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
import genanki

class FlashcardModel(BaseModel):
    """A flashcard with a question and an answer."""
    front: str
    back: str

class OperatorOutput(BaseModel):
    flashcards: list[FlashcardModel]

class SupervisorOutput(BaseModel):
    is_approved: bool = Field(description="True if the flashcards accurately and thoroughly represent the task material.")
    feedback: str = Field(description="Detailed critiques if rejected, empty string if approved.")

class AgentState(TypedDict):
    input_text: str
    output: list[FlashcardModel]
    feedback: str
    is_approved: bool
    revision_count: int

MAX_REVISION_COUNT = 2

with open("prompts/OPERATOR_PROMPT.md") as f:
    OPERATOR_SYSTEM_PROMPT = f.read()

with open("prompts/SUPERVISOR_PROMPT.md") as f:
    SUPERVISOR_SYSTEM_PROMPT = f.read()

def main():
    model = ChatOllama(
        model="mistral:latest",
        temperature=0,
    )

    operator_chain = model.with_structured_output(OperatorOutput)
    supervisor_chain = model.with_structured_output(SupervisorOutput)

    input_file = input("Enter Input File Path: ")
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = f.read()

    print()
    print("Input data loaded successfully.")
    print()
    deck_name = input("Enter Anki Deck Name: ")
    print()

    def operator_node(state: AgentState):
        revision_count = state["revision_count"]
        feedback = state["feedback"]

        if not feedback:
            user_prompt = f"Create 8 flashcards covering this content:\n\n{state["input_text"]}"
        else:
            user_prompt = (
                f"Original Source Content:\n{state['input_text']}\n\n"
                f"Previous Feedback to Fix:\n{feedback}\n\n"
                "Regenerate the flashcards addressing all feedback."
            )

        res: OperatorOutput = operator_chain.invoke([
            SystemMessage(content=OPERATOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        return {
            "output": res.flashcards,
            "revision_count": revision_count + 1
        }

    def supervisor_node(state: AgentState):
        output = state["output"]

        user_prompt = (
            f"Original Source Material:\n{state['input_text']}\n\n"
            f"Generated Flashcards:\n{output}"
        )

        res: SupervisorOutput = supervisor_chain.invoke([
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        return {
            "is_approved": res.is_approved,
            "feedback": res.feedback
        }

    def router(state: AgentState) -> Literal["operator_node", "__end__"]:
        if state["is_approved"] or state["revision_count"] >= MAX_REVISION_COUNT:
            return END
        return "operator_node"

    builder = StateGraph(AgentState)
    builder.add_node(operator_node)
    builder.add_node(supervisor_node)

    builder.add_edge(START, "operator_node")
    builder.add_edge("operator_node", "supervisor_node")
    builder.add_conditional_edges("supervisor_node", router)

    graph = builder.compile()

    initial_state: AgentState = {
        "input_text": input_data,
        "output": [],
        "feedback": "",
        "is_approved": False,
        "revision_count": 0
    }

    final_state = graph.invoke(initial_state)

    # Anki Export
    MODEL_ID = random.randrange(1 << 30, 1 << 31)
    DECK_ID = random.randrange(1 << 30, 1 << 31)

    anki_model = genanki.Model(
        MODEL_ID,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<div style="text-align: center; font-size: 20px;">{{Question}}</div>',
                'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: center; font-size: 20px;">{{Answer}}</div>',
            },
        ]
    )

    anki_deck = genanki.Deck(
        DECK_ID,
        deck_name,
    )

    for flashcard in final_state["output"]:
        anki_note = genanki.Note(
            model=anki_model,
            fields=[flashcard.front, flashcard.back]
        )
        anki_deck.add_note(anki_note)

    genanki.Package(anki_deck).write_to_file(f"outputs/{deck_name}.apkg")

    print("Successfully Exported Anki Package.")

if __name__ == "__main__":
    main()
