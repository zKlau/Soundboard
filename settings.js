const fs = require('fs')


var settingsJson;
function readDevices(){
    fs.readFile('./mainSound/json/devices.json', 'utf8', (err, data) => {
        if (err) {
            console.log(`Error reading file from disk: ${err}`);
        } else {
            json = JSON.parse(data)
            input = json["inputDevices"][0]
            output = json["outputDevices"][0]
            Object.entries(input).forEach(v =>{ 
                document.getElementById("inputDevice").innerHTML += `<option value="${v[1]}">${v[0]}</option>`;
            });
            Object.entries(output).forEach(v =>{ 
                document.getElementById("outputDevice").innerHTML += `<option value="${v[1]}">${v[0]}</option>`;
            });
            console.log(input)
        }

    });
}

function loadSettings() {
    fs.readFile('./mainSound/json/settings.json', 'utf8', (err, data) => {
        if (err) {
            console.log(`Error reading file from disk: ${err}`);
        } else {
            settingsJson = JSON.parse(data)
        }
    
    });
}

function saveDevices(data,device) {
    settingsJson["saved"][0][device] = parseInt(data)
    var data = JSON.stringify(settingsJson,null,2);
    fs.writeFile('./mainSound/json/settings.json', data, 'utf8', (err) => {

        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            
        }
    });
}
$(document).on("click","#saveInput", function() {
    newValue = document.getElementById("inputDevice").value
    saveDevices(newValue,"inputMic")
})
$(document).on("click","#saveOutput", function() {
    newValue = document.getElementById("outputDevice").value
    saveDevices(newValue,"outputMic")
})
readDevices()
loadSettings()