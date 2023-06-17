
import random
import numpy as np
from itertools import chain

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
        :param states: list of states
        :param alphabet: list of symbols
        :param transitions: dict of transitions
        :param start_state: start state
        :param accepting_states: list of accepting states
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = accepting_states
        self.extra_state = 'ε'
        self.reachable_states = list(self.__get_reachable_states())


    def __get_reachable_states(self):
        reachable_states = set()
        reachable_states.add(self.start_state)
        
        # Iteratively find reachable states
        while True:
            new_states = set()
            for state in reachable_states:
                if state in self.transitions:
                    new_states.update(list(chain.from_iterable(self.transitions[state].values())))
            new_states.difference_update(reachable_states)
            if not new_states:
                break
            reachable_states.update(new_states)
        
        return reachable_states
    

    def __epsilon_closure(self, states):
        """
        Một tập hợp các state có thể đạt được từ state A chỉ với epsilon 
        (bao gồm cả A)
        """
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
        new_start_state = frozenset(self.__epsilon_closure(self.start_state))

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
                
                next_states = frozenset(self.__epsilon_closure(next_states))
                new_transitions[current_state].setdefault(symbol, {next_states})
                
                # Thêm tập trạng thái mới vào danh sách chưa đánh dấu
                if next_states not in new_states and next_states != frozenset():
                    unmarked_states.append(next_states)

        new_FA = FA(list(new_states), self.alphabet, new_transitions, new_start_state, list(new_accepting_states))
        # print("NFA converted to DFA.")
        return True, new_FA


    def __complete_otomat(self):
        """
            Đầy đủ hóa otomat đơn định
        """
        for state in self.states:
            if state not in self.transitions:
                self.transitions[state] = {}

            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    self.transitions[state][symbol] = [self.extra_state]
                    if self.extra_state not in self.states:
                        self.states.append(self.extra_state)

                elif len(self.transitions[state][symbol]) == 0:
                    self.transitions[state][symbol] = [self.extra_state]
                    if self.extra_state not in self.states:
                        self.states.append(self.extra_state)


    def __table_mark(self):
        """
            Tạo bảng đánh dấu
        """

        table_size = len(self.reachable_states)
        table = np.zeros((table_size, table_size), dtype = bool)

        while True:
            unmarkable = True
            for i in range(len(self.reachable_states)):
                for j in range(len(self.reachable_states)):

                    if table[i][j]:
                        continue

                    if (
                        self.reachable_states[i] in self.accepting_states and 
                        self.reachable_states[j] not in self.accepting_states
                    ):
                        unmarkable = False
                        table[i][j] = 1
                    else:
                        for symbol in self.alphabet:
                            temp_state_1 = self.transitions[self.reachable_states[i]][symbol][0]
                            temp_state_2 = self.transitions[self.reachable_states[j]][symbol][0]

                            if (
                                table[self.reachable_states.index(temp_state_1)][self.reachable_states.index(temp_state_2)] or 
                                table[self.reachable_states.index(temp_state_2)][self.reachable_states.index(temp_state_1)]
                            ):
                                unmarkable = False
                                table[i][j] = 1
                                break
            if unmarkable:
                break

        return table


    def __unmarked_group(self, table):
        """
            Gộp những điểm đánh dấu trong bảng
        """
        unmarked_states_group = []
        for i in range(len(self.reachable_states)):
            for j in range(len(self.reachable_states)):
                if i == j:
                    continue
                if table[i][j] == 0:
                    if [self.reachable_states[i], self.reachable_states[j]] and [self.reachable_states[j], self.reachable_states[i]] not in unmarked_states_group:
                        check = False
                        for k in range(len(unmarked_states_group)):
                            if self.reachable_states[i] in unmarked_states_group[k] or self.reachable_states[j] in unmarked_states_group[k]:
                                check = True
                                unmarked_states_group[k].extend([self.reachable_states[i], self.reachable_states[j]])
                                unmarked_states_group[k] = list(set(unmarked_states_group[k]))
                                break
                        if not check:
                            unmarked_states_group.append([self.reachable_states[i], self.reachable_states[j]])
        return unmarked_states_group


    def minimize(self):
        """
            Tối thiểu hóa DFA
        """

        if not self.is_DFA():
            return False, "This Automata is not a DFA."

        self.__complete_otomat()
        table = self.__table_mark()
        unmarked_states_group = self.__unmarked_group(table)
        markable_states = [state for state in self.reachable_states if state not in chain.from_iterable(unmarked_states_group)]

        new_states = [x for x in markable_states]
        new_transitions = {}
        for _state in markable_states:
            new_transitions[_state] = self.transitions[_state]

        new_accepting_states = [x for x in self.accepting_states]

        new_start_state = self.start_state

        for group in unmarked_states_group:
            # Tạo trạng thái mới và thay thế trạng thái cũ
            new_state = frozenset(group)
            new_states.append(new_state)
            new_transitions[new_state] = {}
            if self.start_state in group:
                new_start_state = new_state

            for state in group:
                for symbol in self.alphabet:
                    if symbol not in new_transitions[new_state]:
                        new_transitions[new_state][symbol] = []
                    new_transitions[new_state][symbol] += self.transitions[state][symbol]

        # Thay thế trạng thái cũ trong bảng chuyển trạng thái
        for i in range(len(new_states)):
            for j in range(len(self.alphabet)):
                for idx, next_state in enumerate(new_transitions[new_states[i]][self.alphabet[j]]):
                    if next_state not in new_states:
                        for new_state in new_states:
                            if next_state in new_state:
                                new_transitions[new_states[i]][self.alphabet[j]][idx] = new_state
                new_transitions[new_states[i]][self.alphabet[j]] = list(set(new_transitions[new_states[i]][self.alphabet[j]]))


        # Thay thế trạng thái cũ trong tập trạng thái kết
        for idx, final_state in enumerate(self.accepting_states):
            if final_state not in new_states:
                for i in range(len(new_states)):
                    if final_state in new_states[i]:
                        new_accepting_states.append(new_states[i])
        new_accepting_states = list(set(new_accepting_states))

        return True, FA(new_states, self.alphabet, new_transitions, new_start_state, new_accepting_states)


def convert_output(output):

    result = {}

    for attr in output:
        if isinstance(output[attr], (set, list)):
            values = list(output[attr])
            result.setdefault(attr, [])
            for v in values:
                if isinstance(v, (set, frozenset, list)):
                    result[attr].append('+'.join(v))
                else:
                    result[attr].append(v)

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
        else:
            result[attr] = output[attr]

    result['alphabet'] = sorted(result['alphabet'])
    result['states'] = sorted(result['states'], key=lambda x: x == result['startState'], reverse=True)
    return result


# ========================================== #
#                    APIS                    #
# ========================================== #


@api_blp.route('/converter', methods=['GET', 'POST'])
@json_required
def converter():
    try:
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
        
        fa = FA(states, alphabet, _trans, start_state, accept_states)

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
    except Exception as e:
        return bad_request()


@api_blp.route('/minimize', methods=['GET', 'POST'])
@json_required
def minimize():
    try:
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
                _trans[state][symbol] = list(path[symbol])
        
        fa = FA(states, alphabet, _trans, start_state, accept_states)

        try:
            status, mini = fa.minimize()
            if not status:
                return bad_request(mini)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return bad_request('Something went wrong.')
        
        mini_convert_json = convert_output(mini.to_json())

        # key: alphabet, value: state
        state_text_data = {}
        for state in mini_convert_json['transitions']:
            state_text_data.setdefault(state, {})
            state_text_data[state]['acceptStates'] = state in mini_convert_json['acceptStates']
            for key, value in mini_convert_json['transitions'][state].items():
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
            "fsa": mini_convert_json,
        }

        return response(resp)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return bad_request()
