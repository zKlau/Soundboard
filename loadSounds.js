const fs = require('fs');
const ipc = require('electron').ipcRenderer;

document.getElementById("main").innerHTML = ""
fs.readFile('./mainSound/json/sounds.json', 'utf8', (err, data) => {
    if (err) {
        console.log(`Error reading file from disk: ${err}`);
    } else {

        // parse JSON string to JSON object
        const sounds = JSON.parse(data);

        // print all databases
        var defaultData = `class="btn btn-primary" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasRight" aria-controls="offcanvasRight"`
        document.getElementById("main").innerHTML += `<button class="btn btn-primary soundButton"  id="AddSoundButton" onclick="addButton()" style="height: 75px; width: 75px;">+</button>`
        for(var i = 0; i < sounds["sounds"].length; i++) {
            document.getElementById("main").innerHTML += `<button class="btn btn-primary soundButton" id="${i}sound" data-soundPath="${sounds["sounds"][i]["file"]}" data-keybind="${sounds["sounds"][i]["keybind"]}" data-volume="${sounds["sounds"][i]["volume"]}" keycode-values="${sounds["sounds"][i]["keycode"]}" data-id="${i}sound" onclick="SongSideMenu('${i}sound')" data-soundPath="" style="height: 100px; width: 100px;">${sounds["sounds"][i]["name"]}</button>`
        }
        
    }

});

