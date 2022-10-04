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

var settingsJson
function loadSettings() {
    fs.readFile('./mainSound/json/settings.json', 'utf8', (err, data) => {
        if (err) {
            console.log(`Error reading file from disk: ${err}`);
        } else {
            settingsJson = JSON.parse(data)
            $('#muteSounds')[0].checked = settingsJson["saved"][0]["muted"]
            if ($('#muteSounds')[0].checked == false) {
                $('#muteSounds').prop('checked', false).change()
            }
        }
    
    });
}
loadSettings()
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

function saveDevices(data) {
    settingsJson["saved"][0]["muted"] = data
    var data = JSON.stringify(settingsJson,null,2);
    fs.writeFile('./mainSound/json/settings.json', data, 'utf8', (err) => {

        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            
        }
    });
}
$('#muteSounds').change(function() {
    if(this.checked) {
        saveDevices(true)
    } else {
        saveDevices(false)
    }

})

$(document).click((event) => {
    console.log(event.target.id)
    if(event.target.id == "main") {
        disableKeyListen("true")
    } 
})

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
