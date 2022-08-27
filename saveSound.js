const fs = require('fs');
var sounds;
const ipc = require('electron').ipcRenderer;


function readJson(){
    fs.readFile('./mainSound/json/sounds.json', 'utf8', (err, data) => {
        if (err) {
            console.log(`Error reading file from disk: ${err}`);
        } else {
            sounds = JSON.parse(data);
        }
    });
}
readJson()

document.getElementById('fileExplorer').addEventListener('click', openExplorer);

function removeItem() {
    document.getElementById("main").innerHTML = ""
    ipc.send('eventLoadSongs')
    

    ipc.once('loadSongs', function(event, response){
        console.log(response)
        document.getElementById("main").innerHTML = ""
        fs.readFile('./mainSound/json/sounds.json', 'utf8', (err, data) => {
            if (err) {
                console.log(`Error reading file from disk: ${err}`);
            } else {
                const sounds = JSON.parse(data);
        
                var defaultData = `class="btn btn-primary" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasRight" aria-controls="offcanvasRight"`
                document.getElementById("main").innerHTML += `<button class="btn btn-primary soundButton"  style="height: 100px; width: 100px;">+</button>`
                for(var i = 0; i < sounds["sounds"].length; i++) {
                    document.getElementById("main").innerHTML += `<button class="btn btn-primary soundButton" id="${i}sound" data-soundPath="${sounds["sounds"][i]["file"]}" data-keybind="${sounds["sounds"][i]["keybind"]}" data-volume="${sounds["sounds"][i]["volume"]}" data-id="${i}sound" onclick="SongSideMenu('${i}sound')" data-soundPath="" style="height: 100px; width: 100px;">${sounds["sounds"][i]["name"]}</button>`
                }
            }
        });
    })
}


function writeJson() {
    var data = JSON.stringify(sounds, null,2).replaceAll("null,", "").replaceAll(null,"");
    fs.writeFile('./mainSound/json/sounds.json', data, 'utf8', (err) => {

        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            ipc.send('eventLoadSongs')
            readJson()
        }
    });
    removeItem()
    
}
//document.getElementById('DeleteSoundSettings').addEventListener('click', removeItem);
//document.getElementById('AddSound').addEventListener('click', removeItem);

function openExplorer() {
    var songId = document.getElementById("songName").getAttribute("data-id")
    ipc.send('openExplorer')
    
    ipc.once('actionReply', function(event, response){
        console.log(songId)
        //document.getElementById(songId).setAttribute("data-soundPath", response)
        document.getElementById("songName").setAttribute("data-soundPath", response)
    })
}


document.getElementById("SaveSoundSettings").addEventListener("click", function() {
    var vol = document.getElementById("soundVolume").value
    var keybind = document.getElementById("keybindText").getAttribute("key-values")
    var songId = document.getElementById("songName").getAttribute("data-id")
    var id = parseInt(songId.replace("sound",""))
    let checker = (arr, target) => target.every(v => arr.includes(v));
    
    for(var i = 0; i < sounds["sounds"].length; i++) {
        if(sounds["sounds"][i]["keybind"].length == keybind.length) {
            if(checker(sounds["sounds"][i]["keybind"], keybind.split(","))) {
                ipc.send('keybindError')
                return
            }
        }
        if (sounds["sounds"][i]["keybind"] == keybind && id != i++) {
            ipc.send('keybindError')
            return
        }
    }
    
    var name = document.getElementById("songName").value
    var keycode = document.getElementById("keybindText").getAttribute("keycode-values")
    var songId = document.getElementById("songName").getAttribute("data-id")
    //var file = document.getElementById(songId).getAttribute("data-soundPath")

    var id = parseInt(songId.replace("sound",""))
    sounds["sounds"][id]["volume"] = vol / 100
    sounds["sounds"][id]["keybind"] = keybind
    sounds["sounds"][id]["name"] = name
    //sounds["sounds"][id]["file"] = file
    sounds["sounds"][id]["keycode"] = keycode
    writeJson()
    
})

document.getElementById("AddSound").addEventListener("click", function() {
    var vol = document.getElementById("soundVolume").value
    var keybind = document.getElementById("keybindText").getAttribute("key-values")

    for(var i = 0; i < sounds["sounds"].length; i++) {
        if (sounds["sounds"][i]["keybind"] == keybind) {
            ipc.send('keybindError')
            return
        }
    }
    var name = document.getElementById("songName").value
    var keycode = document.getElementById("keybindText").getAttribute("keycode-values")
    //var songId = document.getElementById("songName").getAttribute("data-id")
    var file = document.getElementById("songName").getAttribute("data-soundPath")

    //var id = parseInt(songId.replace("sound",""))
    var newSound = {
        "name": name,
        "file": file,
        "keycode": keycode,
        "keybind": keybind,
        "volume": vol/100
    }
    sounds["sounds"].push(newSound)
    writeJson()
    
})

document.getElementById("DeleteSoundSettings").addEventListener("click", function() {
    var songId = document.getElementById("songName").getAttribute("data-id")
    console.log(sounds["sounds"])
    var id = parseInt(songId.replace("sound",""))
    delete sounds["sounds"][id]
    sounds["sounds"] = sounds["sounds"].filter(x => x != null)
    
    writeJson()
    
})


