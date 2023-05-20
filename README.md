# Automata - Visual DFA Converter

## Overview
<img alt="Screenshot of the main application interface" src="https://i.imgur.com/G38tE90.png">

This tool is used to convert [non-deterministic finite automata](https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton) (NFA) to [deterministic finite automata](https://en.wikipedia.org/wiki/Deterministic_finite_automaton) (DFA) through an interactive and visual interface.

### Technology
<img src="https://i.imgur.com/vCfnuNM.png" alt= “fe-tech” width="300 px">

<img src="https://i.imgur.com/XVwufwD.png" alt= “fe-tech” width="95 px">

### Reference
UI/UI I used and custom in [nfa-to-dfa](https://github.com/joeylemon/nfa-to-dfa)

## Running Application

1. **Clone repository**

    To set up app in your local, first clone this repository:
    ```shell
    git clone https://github.com/quanpersie2001/DFA-Converter
    ```
1. **Creat & activate virtual environment**
    ```shell
    python -m venv venv
    ```
    Active `venv`
    ```shell
    venv/Scripts/activate
    ```
2. **Install dependencies**
    ```shell
    pip install -r requirements.txt
    ```
2. **Set environment variables**
    ```shell
    set_env.ps1
    ```
3. **Run server**
    ```shell
    flask run --port=8000
    ```
    Running this script should give an output similar to below:
    ```
    * Serving Flask app 'application.py'
    * Debug mode: on
    [2023-05-21 03:19:10] INFO _internal.py line 224: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:8000
    [2023-05-21 03:19:10] INFO _internal.py line 224: Press CTRL+C to quit
    [2023-05-21 03:19:10] INFO _internal.py line 224:  * Restarting with stat
    [2023-05-21 03:19:11] WARNING _internal.py line 224:  * Debugger is active!
    [2023-05-21 03:19:11] INFO _internal.py line 224:  * Debugger PIN: 139-055-000
    ```
    You can now navigate to http://localhost:8000 in the browser to view the application.