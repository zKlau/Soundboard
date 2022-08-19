var exec = require('child_process').spawn;
const nt = require('ntsuspend');
const fs = require('fs');
const ipc = require('electron').ipcRenderer;
var keys = [];
var key_values = []
var keycode_values = []

var allowKeybind = false
exec("mainSound.exe", { cwd: "mainSound"})

function writeJson(input) {
    fs.writeFile('./mainSound/json/readInput.json', input, 'utf8', (err) => {
        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            ipc.send('eventLoadSongs')
        }
    });
}

$(document).on("click","#keybindEnable", function() {
    console.log(allowKeybind)
    if(allowKeybind == true) {
        allowKeybind = false
        document.getElementById("keybindEnable").innerHTML = "Select Keybind"
        writeJson("true")
    } else {
        document.getElementById("keybindEnable").innerHTML = "Selecting Keybind"
        writeJson("false")
        allowKeybind = true
    }
})

    $(document).ready(function(){
        $(document).on('keydown', function(e){
            if(allowKeybind){
                if (!key_values.includes(e.key) || !keycode_values.includes(e.keyCode)){
                    e = (e) ? e : ((event) ? event : null);
                    if (keys.length < 3) {
                        if(e.keyCode >= 96 && e.keyCode <= 105)
                        {
                            keys.push("NUM " + e.key)
                        } else {
                            keys.push(e.key)
                        }
                        keycode_values.push(e.keyCode)

                        if (e.key == "Control"){
                            key_values.push("ctrl")
                        } else if (e.key == "Alt") {
                            key_values.push("alt")
                        } else {
                            key_values.push((e.keyCode >= 96 && e.keyCode <= 105) ? "NUM " + e.key : e.key)
                        }
                        console.log(e.key, e.keyCode)
                        document.getElementById("keybindText").value = keys.join(" + ")
                        document.getElementById("keybindText").setAttribute("key-values",key_values)
                        document.getElementById("keybindText").setAttribute("keycode-values",keycode_values)
                    }
                    
                }
            }        
        });
});
$(document).ready(function(){
    $(document).on('keyup', function(e){
      keys = []
      key_values = []
      keycode_values = []
    });
});