# PAD Monster WebApp

A simple web application for searching and viewing Puzzle and Dragons monster information. It is built on [Flask](http://flask.pocoo.org/), a Python microframework.

The data back-end is hosted at [PAD Data](https://github.com/jutongpan/paddata).

The [old version](https://github.com/jutongpan/padmonsterShiny) of the app is based on R Shiny framework. I decided to move away from Shiny to Flask because Shiny applications get disconnected when the app is in background on iOS devices. (Shiny relies on the Websocket protocol to maintain the session connection and iOS disables Websocket running on the background.) Flask, on the other hand, is RESTful.
