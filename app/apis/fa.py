
import random
from flask import request
from app.apis import api_blp
from app.decorators import json_required
from app.utils import bad_request, response

class FA:
    """
    Finite Automata
    """
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        """
        :param states: set of states
        :param alphabet: set of symbols
        :param transitions: dict of transitions
        :param start_state: start state
        :param accepting_states: set of accepting states
        """
        self.states = states
        self.alphabet = alphabet
        # self.alphabet.add('ε')
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = accepting_states
    

    def epsilon_closure(self, states):
        closure = set(states)
        if isinstance(states, str):
            states = {states}
        queue = list(states)
        while queue:
            current_state = queue.pop(0)
            if current_state in self.transitions and 'ε' in self.transitions[current_state]:
                for next_state in self.transitions[current_state].get('ε'):
                    if next_state not in closure:
                        closure.add(next_state)
                        queue.append(next_state)
        return frozenset(closure)


    def accept(self, input_string):
        current_states = {self.start_state}
        for symbol in input_string:

            if symbol not in self.alphabet:
                return False

            next_states = set()
            for state in current_states:
                
                if state not in self.transitions:
                    return False
                
                if symbol in self.transitions[state]:
                    st = self.transitions[state][symbol]
                    if isinstance(st, set):
                        next_states.update(st)
                    elif isinstance(st, str):
                        next_states.add(st)
                    elif isinstance(st, frozenset):
                        next_states.update(st)

            current_states = next_states
            
            if not current_states:
                return False


    def is_DFA(self):
        for st in self.transitions:
            if 'ε' in self.transitions.get(st).keys():
                return False
        for state in self.states:
            for symbol in self.alphabet:
                trans = self.transitions.get(state, None)
                if not trans:
                    continue
                if symbol not in trans:
                    continue
                if len(self.transitions[state][symbol]) != 1:
                    return False
        return True
    

    def to_json(self):
        return {
            'states': self.states,
            'alphabet': self.alphabet,
            'transitions': self.transitions,
            'startState': self.start_state,
            'acceptStates': self.accepting_states
        }
    

    def to_DFA(self):
        if self.is_DFA():
            return False, "This Automata is already a DFA."

        new_states = set()
        new_transitions = {}
        new_accepting_states = set()
        new_start_state = frozenset(self.epsilon_closure(self.start_state))

        # Tạo tập trạng thái đầu tiên cho DFA
        unmarked_states = [new_start_state]

        while unmarked_states:
            current_state = unmarked_states.pop()
            new_states.add(current_state)

            # Xác định trạng thái kết thúc của DFA
            if any(state in current_state for state in self.accepting_states):
                new_accepting_states.add(current_state)

            # Tạo bảng chuyển tiếp cho tập trạng thái hiện tại
            new_transitions[current_state] = {}
            for symbol in self.alphabet:
                next_states = set()

                for state in current_state:
                    __ = self.transitions.get(state, dict()).get(symbol, set())
                    if isinstance(__, set):
                        next_states.update(__)

                    elif isinstance(__, str):
                        next_states.add(__)
                    
                if not next_states:
                    continue
                
                next_states = frozenset(self.epsilon_closure(next_states))
                new_transitions[current_state].setdefault(symbol, {next_states})
                
                # Thêm tập trạng thái mới vào danh sách chưa đánh dấu
                if next_states not in new_states and next_states != frozenset():
                    unmarked_states.append(next_states)

        new_FA = FA(new_states, self.alphabet, new_transitions, new_start_state, new_accepting_states)
        # print("NFA converted to DFA.")
        return True, new_FA
    

def convert_output(output):

    result = {}

    for attr in output:
        if isinstance(output[attr], set):
            values = list(output[attr])
            result.setdefault(attr, [])
            for v in values:
                result[attr].append('+'.join(v))
        elif isinstance(output[attr], dict):
            values = output[attr]
            result.setdefault(attr, {})
            for k in values:
                key = '+'.join(k)
                result[attr].setdefault(key, {})
                for alphabet in values[k]:
                    result[attr][key].setdefault(alphabet, [])
                    for v in values[k][alphabet]:
                        result[attr][key][alphabet].append('+'.join(v))
        elif isinstance(output[attr], frozenset):
            result.setdefault(attr, '+'.join(output[attr]))
    result['alphabet'] = sorted(result['alphabet'])
    result['states'] = sorted(result['states'], key=lambda x: x == result['startState'], reverse=True)
    return result


@api_blp.route('/converter', methods=['GET', 'POST'])
@json_required
def converter():
    data = request.json.get("input")
    input = data.get('fsa')

    states = input.get('states')
    alphabet = input.get('alphabet')
    transitions = input.get('transitions')
    start_state = input.get('startState')
    accept_states = input.get('acceptStates')

    if not states:
        return bad_request("Missing states")
    if not alphabet:
        return bad_request("Missing alphabet")
    if not transitions:
        return bad_request("Missing transitions")
    if not start_state:
        return bad_request("Missing start state")
    if not accept_states:
        return bad_request("Missing accept states")
    
    _trans = {}
    
    for state in states:
        path = transitions.get(state)
        if not path:
            continue
        _trans.setdefault(state, {})
        for symbol in path:
            _trans[state][symbol] = set(path[symbol])
    
    fa = FA(set(states), set(alphabet), _trans, start_state, set(accept_states))

    try:
        status, dfa = fa.to_DFA()
        if not status:
            return bad_request(dfa)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return bad_request('Something went wrong.')
    
    dfa_convert_json = convert_output(dfa.to_json())

    # key: alphabet, value: state
    state_text_data = {}
    for state in dfa_convert_json['transitions']:
        state_text_data.setdefault(state, {})
        state_text_data[state]['acceptStates'] = state in dfa_convert_json['acceptStates']
        for key, value in dfa_convert_json['transitions'][state].items():
            for _st in value:
                state_text_data[state].setdefault(_st, [])
                state_text_data[state][_st].append(key)

    node = [
        {
        "label": f"{state}" if state else "Ø",
        "loc": {
            "x": random.randint(50, 700),
            "y": random.randint(50, 700)
        },
        "transitionText": {
            k: v for k, v in state_text_data.get(state).items() if k != 'acceptStates'
        },
        "acceptState": state_text_data.get(state).get('acceptStates')
        }
        for state in state_text_data
    ]

    resp = {
        "nodes": node,
        "fsa": dfa_convert_json,
    }

    return response(resp)
