
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Halting Boundary Tracker",
    page_icon="💻",
    layout="wide"
)

# -------------------------------
# SESSION STATE
# -------------------------------
if "simulation_result" not in st.session_state:
    st.session_state["simulation_result"] = None

if "is_playing" not in st.session_state:
    st.session_state["is_playing"] = False

if "tape_step_slider" not in st.session_state:
    st.session_state["tape_step_slider"] = 0

# -------------------------------
# TITLE
# -------------------------------
st.title("💻 Halting Boundary Tracker")

st.write(
    "A Turing Machine Simulation Sandbox "
    "with a Bounded Execution Limit"
)

st.info(
    "Simulate a Turing Machine for at most K transitions. "
    "The input tape accepts only 0 and 1, with a maximum "
    "length of 20 symbols."
)

# -------------------------------
# STATE DIAGRAM
# -------------------------------
st.subheader("1. Turing Machine State Diagram")

st.graphviz_chart("""
digraph TM {
    rankdir=LR;
    bgcolor="transparent";
    node [fontname="Arial", style=filled, fillcolor=lightblue];

    start [shape=point];
    q0 [shape=circle, label="q0\\nScanning"];
    halt [shape=doublecircle, label="HALT"];

    start -> q0;
    q0 -> q0 [label="0 / 0, R"];
    q0 -> q0 [label="1 / 1, R"];
    q0 -> halt [label="Blank"];
}
""")

st.caption(
    "The machine scans the tape from left to right "
    "and enters HALT when it reaches a blank cell."
)

# -------------------------------
# INPUT CONFIGURATION
# -------------------------------
st.subheader("2. Input Configuration")

tape_input = st.text_input(
    "Enter binary input tape (0 and 1 only)",
    value="10101",
    max_chars=20,
    key="tape_input",
    help="Enter between 1 and 20 binary symbols."
)

st.caption(f"Input length: {len(tape_input)} / 20 symbols")

k = st.number_input(
    "Maximum execution steps (K)",
    min_value=0,
    max_value=1000,
    value=10,
    step=1,
    key="step_limit"
)

st.write("**Initial state:** q0")
st.write("**Halt state:** HALT")
st.write("**Head movement:** Right (R)")

# -------------------------------
# SIMULATION FUNCTION
# -------------------------------
def simulate_tm(input_tape, max_steps):

    tape = list(input_tape) + ["_"]
    head = 0
    state = "q0"
    steps = 0
    history = []

    while True:

        if state == "HALT":
            status = "HALTED"
            break

        if steps >= max_steps:
            status = "TIMEOUT"
            break

        symbol = tape[head]

        # Record the current configuration
        history.append({
            "Step": steps,
            "State": state,
            "Tape": "".join(tape),
            "Head Position": head,
            "Read Symbol": (
                "Blank" if symbol == "_" else symbol
            )
        })

        # Read a binary symbol and move right
        if state == "q0" and symbol in ("0", "1"):
            head += 1
            steps += 1

        # Blank cell causes the machine to halt
        elif state == "q0" and symbol == "_":
            state = "HALT"
            steps += 1

        else:
            status = "STUCK"
            break

    # Record final configuration
    final_symbol = tape[head]

    history.append({
        "Step": steps,
        "State": state,
        "Tape": "".join(tape),
        "Head Position": head,
        "Read Symbol": (
            "Blank" if final_symbol == "_" else final_symbol
        )
    })

    return status, steps, state, tape, head, history

# -------------------------------
# RUN / RESET BUTTONS
# -------------------------------
run_col, reset_col = st.columns(2)

with run_col:
    run_clicked = st.button(
        "▶ Run Simulation",
        type="primary",
        use_container_width=True
    )

with reset_col:
    reset_clicked = st.button(
        "↻ Reset",
        use_container_width=True
    )

if reset_clicked:
    st.session_state["simulation_result"] = None
    st.session_state["is_playing"] = False
    st.session_state["tape_input"] = "10101"
    st.session_state["step_limit"] = 10
    st.session_state["tape_step_slider"] = 0
    st.rerun()

# -------------------------------
# VALIDATE AND RUN
# -------------------------------
if run_clicked:

    st.session_state["is_playing"] = False
    st.session_state["simulation_result"] = None
    st.session_state["tape_step_slider"] = 0

    if not tape_input:
        st.error("INVALID INPUT: The tape cannot be empty.")

    elif any(symbol not in "01" for symbol in tape_input):
        st.error("INVALID INPUT: Enter only 0 and 1.")

    else:
        result = simulate_tm(tape_input, int(k))

        st.session_state["simulation_result"] = {
            "input": tape_input,
            "k": int(k),
            "result": result
        }

# -------------------------------
# CHECK SAVED RESULT
# -------------------------------
saved = st.session_state["simulation_result"]

if saved is not None and (
    saved["input"] != tape_input
    or saved["k"] != int(k)
):
    st.session_state["is_playing"] = False
    st.info("Input or K changed. Click Run Simulation again.")
    saved = None

# -------------------------------
# DISPLAY RESULTS
# -------------------------------
if saved is not None:

    status, steps, state, tape, head, history = saved["result"]

    st.subheader("3. Simulation Result")

    c1, c2, c3 = st.columns(3)
    c1.metric("Execution Steps", steps)
    c2.metric("Maximum Steps (K)", int(k))
    c3.metric("Input Length", len(tape_input))

    if status == "HALTED":
        st.success("HALTED: The machine reached its halt state.")

    elif status == "TIMEOUT":
        st.warning(
            "TIMEOUT: The machine did not halt within K steps. "
            "This does not prove it will never halt."
        )

    else:
        st.error("STUCK: No applicable transition was available.")

    st.write(f"**Final state:** {state}")
    st.write(f"**Final tape:** `{''.join(tape)}`")
    st.write(f"**Final head position:** {head}")

    # -------------------------------
    # TAPE DIAGRAM AND ANIMATION
    # -------------------------------
    st.subheader("4. Turing Machine Tape Diagram")

    st.write(
        "Press Play to move the head automatically. "
        "Use Pause to stop or the slider to inspect a step."
    )

    last_step = len(history) - 1

    # Keep slider position within the available steps
    st.session_state["tape_step_slider"] = min(
        st.session_state["tape_step_slider"],
        last_step
    )

    play_col, pause_col, restart_col = st.columns(3)

    with play_col:
        if st.button("▶ Play", use_container_width=True):
            if st.session_state["tape_step_slider"] >= last_step:
                st.session_state["tape_step_slider"] = 0

            st.session_state["is_playing"] = True
            st.rerun()

    with pause_col:
        if st.button("⏸ Pause", use_container_width=True):
            st.session_state["is_playing"] = False
            st.rerun()

    with restart_col:
        if st.button("↻ Restart Animation", use_container_width=True):
            st.session_state["is_playing"] = False
            st.session_state["tape_step_slider"] = 0
            st.rerun()

    # Automatically refresh and advance one step
    if st.session_state["is_playing"]:

        st_autorefresh(
            interval=800,
            limit=None,
            key="tape_animation_refresh"
        )

        if st.session_state["tape_step_slider"] < last_step:
            st.session_state["tape_step_slider"] += 1
        else:
            st.session_state["is_playing"] = False

    # Manual step selection
    selected_step = st.slider(
        "Select execution step",
        min_value=0,
        max_value=last_step,
        step=1,
        key="tape_step_slider"
    )

    frame = history[selected_step]
    current_tape = frame["Tape"]
    current_head = frame["Head Position"]

    st.write(f"**Step:** {frame['Step']}")
    st.write(f"**Current state:** {frame['State']}")
    st.write(f"**Head position:** {current_head}")
    st.write(f"**Symbol read:** {frame['Read Symbol']}")

    # Draw individual tape cells
    cell_columns = st.columns(len(current_tape))

    for i, symbol in enumerate(current_tape):

        with cell_columns[i]:

            if i == current_head:
                st.markdown(
                    f"""
                    <div style="
                        border: 3px solid #2563eb;
                        background-color: #dbeafe;
                        color: #1e3a8a;
                        border-radius: 8px;
                        padding: 12px 2px;
                        text-align: center;
                        font-size: 20px;
                        font-weight: bold;
                    ">{symbol}</div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #9ca3af;
                        border-radius: 8px;
                        padding: 14px 2px;
                        text-align: center;
                        font-size: 20px;
                    ">{symbol}</div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(f"Position {i}")

    st.caption(
        "The blue cell shows the head position. "
        "The underscore (_) represents a blank cell."
    )

    # -------------------------------
    # EXECUTION HISTORY
    # -------------------------------
    st.subheader("5. Execution History")

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True
    )

# -------------------------------
# ABOUT PROJECT
# -------------------------------
with st.expander("About this project"):

    st.write("""
    Project: Halting Boundary Tracker

    Purpose: Simulate a Turing Machine under a finite
    execution-step limit.

    Input: Binary strings containing only 0 and 1,
    with a maximum length of 20 symbols.

    HALTED: The machine reaches its halt state within K steps.

    TIMEOUT: The machine has not halted within K transitions.

    STUCK: No applicable transition is available.

    Limitation: TIMEOUT does not prove that a machine will
    never halt. This app demonstrates bounded simulation
    for one fixed Turing Machine.
    """)
