// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.
const ipc = require('electron').ipcRenderer;
const fs = require('fs');
document.getElementById('close-button').addEventListener('click', closeWindow);
document.getElementById('min-button').addEventListener('click', minimizeWindow);
document.getElementById('max-button').addEventListener('click', maximizeWindow);
document.getElementById('settings').addEventListener('click',openSettings)
document.getElementById('home').addEventListener('click',openHome)
//document.getElementById('themeButton').addEventListener('click',openSettings)
function disableKeyListen(input) {
    fs.writeFile('./mainSound/json/readInput.json', input, 'utf8', (err) => {
        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            ipc.send('eventLoadSongs')
        }
    });
}

disableKeyListen("true")
function closeWindow () {
    ipc.send('close');
}

function openSettings() {
    ipc.send('openSettings')
}
function openHome() {
    ipc.send('mainPage')
}

function minimizeWindow () {  
    ipc.send('min');
}

function maximizeWindow () {
    ipc.send('max');
    //window.isMaximized() ? window.unmaximize() : window.maximize();
}
