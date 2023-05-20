let warningTimeout

// Close a warning when the close button is clicked
document.querySelectorAll('.delete').forEach(e => e.addEventListener('click', e => {
    e.target.parentElement.style.display = 'none'
}))

function syncHeight (selector1, selector2) {
    document.querySelector(selector1).style.height = `${document.querySelector(selector2).clientHeight}px`
}

/**
 * Synchronize the height of element pairs upon window resizing
 *
 * @param {Array} listOfPairs The list of element pairs to keep synced
 */
export function keepHeightSynced (listOfPairs) {
    for (const pair of listOfPairs) {
        syncHeight(pair[0], pair[1])
    }

    window.addEventListener('resize', () => {
        for (const pair of listOfPairs) {
            syncHeight(pair[0], pair[1])
        }
    })
}

/**
 * Display the given warning element with a message
 *
 * @param {String} message The message to put into the warning
 */
export function showWarning (message) {
    document.querySelector('#warning').style.display = 'block'
    document.querySelector('#warning').querySelector('.notification-body').innerHTML = message

    // Delete the warning after a delay
    if (warningTimeout) { clearTimeout(warningTimeout) }
    warningTimeout = setTimeout(() => {
        document.querySelector('#warning').style.display = 'none'
        warningTimeout = undefined
    }, 4000)
}

/**
 * Download a file onto the user's computer
 *
 * @param {String} filename The name of the file to create
 * @param {String} content The string contents of the file
 */
export function downloadFile (filename, content) {
    const dataString = 'data:text/json;charset=utf-8,' + encodeURIComponent(content)
    const downloadNode = document.createElement('a')
    downloadNode.setAttribute('href', dataString)
    downloadNode.setAttribute('download', filename)
    document.body.appendChild(downloadNode)
    downloadNode.click()
    downloadNode.remove()
}

/**
 * Download a file onto the user's computer
 *
 * @param {String} url The url
 * @param {JSON} payload payload
 * @param {?Function} callback callback function
 */
export function sendRequest (url, payload, callback) {
    const errHandling = (err) => {
        showWarning(err)
    }
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8'
        },
        body: JSON.stringify(payload)
    }).then(response => response.json()).then(res => {
        if (res?.status === true) {
            return callback && callback(res.data)
        }
        errHandling(res?.message || 'error')
    }).catch(err => errHandling(err))
}
