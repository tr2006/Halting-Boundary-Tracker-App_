
# Halting Boundary Tracker

## Project Description
The Halting Boundary Tracker is a Python-based application developed using Streamlit to demonstrate the working of a simple Turing Machine and its halting behavior under a given step limit.

## Objectives
- To simulate a Turing Machine.
- To visualize the tape and head movement.
- To demonstrate HALTED and TIMEOUT outcomes.
- To allow users to control the maximum number of transitions.
- To display the execution history and animation.

## Technologies Used
- Python
- Streamlit
- Graphviz
- Streamlit Autorefresh

## How to Run
1. Install Python.
2. Install the required libraries:
   `pip install -r requirements.txt`
3. Run the application:
   `python -m streamlit run app.py`

## Input
The application accepts a binary string containing only 0 and 1, along with a maximum transition limit K.

## Output
The result indicates whether the machine reaches its HALT state within the specified transition limit or returns TIMEOUT.
