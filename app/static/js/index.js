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

function setButtonsState (enabled) {
    document.querySelector('#reset').disabled = !enabled
    document.querySelector('#convert').disabled = !enabled
}

/**
 * Clear
 */
document.querySelector('#reset').addEventListener('click', () => {
    nfa.visual.reset()
    dfa.visual.reset()
})

/**
 * Convert
 */
document.querySelector('#convert').addEventListener('click', () => {
    return utils.sendRequest('/api/converter', {'input' : nfa.visual.toJSON()}, res => {
        dfa.visual.fromCustomJSON(res)
    })
})
