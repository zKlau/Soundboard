const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require('path')
const fs = require('fs');
var exec = require('child_process').spawn;
const nativeImage = require('electron').nativeImage;
    var image = nativeImage.createFromPath(__dirname + '/public/img/icon.png'); 
 // where public folder on the root dir

    image.setTemplateImage(true);

function createWindow() {
    // Create the browser window.
    let win = new BrowserWindow({
        width: 1280,
        height: 720,
        minHeight: 720,
        minWidth: 1280,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
        },
        icon: image,
        frame: false,
        transparent: true
    });
    //win.webContents.setAudioMuted(true)
    win.loadFile("index.html");
    ipcMain.on('max', () => {
        win.isMaximized() ? win.unmaximize() : win.maximize()
    })
    ipcMain.on('min', () => {
        win.minimize()
    })
    ipcMain.on('close', () => {
        win.close()
    })
    
    ipcMain.on('openExplorer', (event)=> {
        dialog.showOpenDialog().then((res) => {
            
            var data = res.filePaths[0].replaceAll("\\","/")
            event.sender.send('actionReply', data);
        })
    })
    ipcMain.on('openSettings', (event) => {
        win.loadFile("settings.html");
    })
    ipcMain.on('mainPage', (event) => {
        win.loadFile("index.html");
    })
    ipcMain.on('keybindError', (event)=> {
        dialog.showErrorBox("Keybind already used!", "Please use another keybind!")
    })

    ipcMain.on('eventLoadSongs', (event)=> {
        event.sender.send('loadSongs',"merge");
    })
}
exec("mainSound.exe", { cwd: "mainSound"})
app.on("ready", createWindow);