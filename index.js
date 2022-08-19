const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require('path')
const fs = require('fs');


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
        frame: false,
        transparent: true,
    });
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

app.on("ready", createWindow);