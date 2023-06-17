import DraggableCanvas from './canvas/draggable_canvas.js'
import VisualFSA from './fsa/visual_fsa.js'
import * as utils from './util/util.js'
import FSADescription from './elements/fsa_description.js'

utils.keepHeightSynced([['#dfa-title', '#nfa-title']])

const nfa = {
    visual: new VisualFSA(new DraggableCanvas('#nfa'), false),
    desc: new FSADescription('#nfa-delta-transitions')
}

const dfa = {
    visual: new VisualFSA(new DraggableCanvas('#dfa'), true),
    desc: new FSADescription('#dfa-delta-transitions')
}

nfa.visual.addEventListener('change', () => {
    if (nfa.visual.fsa.states.length > 0) {
        nfa.desc.update(nfa.visual.fsa, true)
        setButtonsState(true)
    } else {
        nfa.desc.reset()
        setButtonsState(false)
    }
})

dfa.visual.addEventListener('change', () => {
    if (dfa.visual.fsa.states.length > 0) {
        dfa.desc.update(dfa.visual.fsa, false)
    } else {
        dfa.desc.reset()
    }
})

/**
 * Draw the canvas any time there is a change to its elements
 */
draw()
function draw () {
    nfa.visual.draggableCanvas.draw()
    dfa.visual.draggableCanvas.draw()
    window.requestAnimationFrame(draw)
}

const $nfaTitle = document.querySelector('#nfa-title h1');
const $dfaTitle = document.querySelector('#dfa-title h1');
const $resetBtn = document.querySelector('#reset');
const $submitBtn = document.querySelector('#convert');
const $typeSelect = document.querySelector('#select-type');

function setButtonsState (enabled) {
    $resetBtn.disabled = !enabled
    $submitBtn.disabled = !enabled
}

$typeSelect.addEventListener('change', () => {
    if (nfa.visual.fsa.states.length > 0) {
        setButtonsState(true)
    }
    let type = $typeSelect.value;
    if (type === 'converter') {
        $nfaTitle.innerText = 'Finite Automaton (FA)';
        $dfaTitle.innerText = 'Deterministic Finite Automaton (DFA)';
    }
    if (type === 'minimize') {
        $nfaTitle.innerText = 'Deterministic Finite Automaton (DEA)';
        $dfaTitle.innerText = 'Minimized';
    }
})

/**
 * Clear
 */
$resetBtn.addEventListener('click', () => {
    nfa.visual.reset()
    dfa.visual.reset()
})

/**
 * Convert
 */
$submitBtn.addEventListener('click', () => {
    let type = $typeSelect.value;
    $submitBtn.disabled = true;
    return utils.sendRequest(`/api/${type}`, {'input' : nfa.visual.toJSON()}, res => {
        dfa.visual.fromCustomJSON(res)
    })
})
