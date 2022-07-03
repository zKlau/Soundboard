<br/>
<p align="center">
  <a href="https://github.com/zKlau/Soundboard">
    
  </a>

  <h3 align="center">Soundboard</h3>

  <p align="center">
    A Soundboard for windows and android
    <br/>
    <br/>
    <a href="https://github.com/zKlau/Soundboard"><strong>Explore the docs »</strong></a>
    <br/>
    <br/>
    <a href="https://github.com/zKlau/Soundboard/issues">Report Bug</a>
    .
    <a href="https://github.com/zKlau/Soundboard/issues">Request Feature</a>
  </p>
</p>

![Downloads](https://img.shields.io/github/downloads/zKlau/Soundboard/total) ![Contributors](https://img.shields.io/github/contributors/zKlau/Soundboard?color=dark-green) ![Issues](https://img.shields.io/github/issues/zKlau/Soundboard) ![License](https://img.shields.io/github/license/zKlau/Soundboard) 

## Table Of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

With this project we tried to achive what other didn't and that is a soundboard that can be used on your phone and on a computer at the same time. 

## Built With

The Windows variant was built with python and the mobile one with Flutter

## Getting Started


### Prerequisites

To use this we recommend installing https://vb-audio.com/Cable/index.htm
In the future we hope to create our own virtual cable driver.

## Extra settings for the virtual cable
- Right click the volume icon in the right down corner
- Click on "Open sound Setting"
- On the right side click on "Sound Control Panel"
- Go to "Recording Tab"
- Right click on your current microphone and click on "Properties"
- Go to "Listen" tab then click on "Payback through this device" and select "CABLE Input (VB-Audio Virtual Cable)"
- Check the "Listen to this device" box and Apply
!! THIS IS NOT NECESSARY BUT IT IS RECOMMENDED

### Installation

To edit and run the code on your machine first you need to open the terminal in the current directory and run this command
```sh
pip install -r requirements.txt
```
after that use
```sh
python mainSound.py
```

## Usage

This app is used to simulate sound through a virtual microphone. Those sounds can be activated by using a hotkey on your computer or by pressing a button on your phone.

## Authors

* **Claudiu Padure** - *Software Developer* - [Claudiu Padure](https://github.com/zKlau) - *Windows app*
* **Denis Feri** - *Mobile Developer* - [Denis Feri](https://github.com/mrhellou) - *Support for Android*
