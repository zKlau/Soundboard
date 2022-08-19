const fs = require('fs');

var theme = "styles"
var json;
//document.getElementById("head").innerHTML += '<link rel="stylesheet" href="style-green.css" id="theme" />'
function loadTheme() {
    fs.readFile('./mainSound/json/settings.json', 'utf8', (err, data) => {
        if (err) {
            console.log(`Error reading file from disk: ${err}`);
        } else {
            json = JSON.parse(data)
            theme = json["saved"][0]["theme"]
            document.getElementById("head").innerHTML += `<link rel="stylesheet" href="themes/${theme}.css'" id="theme" />`
            document.getElementById("theme").setAttribute("href", "themes/"+theme+".css")
        }
    
    });
}


function saveTheme(data) {
    json["saved"][0]["theme"] = data
    var data = JSON.stringify(json,null,2);
    fs.writeFile('./mainSound/json/settings.json', data, 'utf8', (err) => {

        if (err) {
            console.log(`Error writing file: ${err}`);
        } else {
            
        }
    });
}

$(document).on("click","#themeButton", function() {
    newTheme = document.getElementById("themeButtonSelection").value
    saveTheme(newTheme)

    document.getElementById("theme").setAttribute("href", "themes/" + newTheme + ".css")
})
loadTheme()