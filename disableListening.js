const fs = require('fs');
const ipc = require('electron').ipcRenderer;

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