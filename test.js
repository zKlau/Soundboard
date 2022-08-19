var exec = require('child_process').spawn;
const nt = require('ntsuspend');

var process = exec("mainSound.exe", { cwd: "mainSound"})


function function2() {
    nt.suspend(process.pid);
}

function function3() {
    nt.resume(process.pid);
}
setTimeout(function2, 10000);
setTimeout(function3, 15000);