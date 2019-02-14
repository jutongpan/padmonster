# PAD Monster WebApp

A simple web application for searching and viewing Puzzle and Dragons monster information. It is built on [Flask](http://flask.pocoo.org/), a Python microframework.

The data back-end is hosted at [PAD Data](https://github.com/jutongpan/paddata).

The [old version](https://github.com/jutongpan/padmonsterShiny) of the app is based on R Shiny framework. I decided to move away from Shiny to Flask because Shiny applications get disconnected when the app is in background on iOS devices. (Shiny relies on the Websocket protocol to maintain the session connection and iOS disables Websocket running on the background.) Flask, on the other hand, is RESTful.

## Deployment on Ubuntu (16.04+)
Below is heavily borrowing from the article [How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-16-04). The main difference between the method here and the article is that I use *conda* instead of *virtualenv* to manage environments.

### Install Miniconda3
Want to enjoy the convenience of conda environment management but don't want to install the bloated Anaconda? [Miniconda](https://docs.conda.io/en/latest/miniconda.html) is the way to go.

Miniconda3 is Python3 based. This app is written in Python3. (In fact, you can install Python2 using Miniconda3 as well. It's just that the default Python version for Miniconda3 is Python3)

Installation of Miniconda3 on 64-bit Linux:
```Bash
$ cd ~
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ bash Miniconda3-latest-Linux-x86_64.sh
$ rm Miniconda3-latest-Linux-x86_64.sh
```

### Setup Flask environment
```Bash
$ conda create -n flask
```
This creates a virtual environment named "flask". It's empty at the moment.

```Bash
$ conda activate flask
```
This activates the "flask" environment we just created.

```Bash
$ conda install flask pandas gunicorn -y
```
This installs `flask`, `pandas`, and `gunicorn`, plus a couple of other things, such as Python3, sqlite, mkl, numpy, openssl, etc. Those "other things" are the "basic packages" in all conda environment.

```Bash
$ sudo apt-get install python3-dev nginx
```
Disclaimer: I don't know if `python3-dev` is actually necessary.

### Clone this app
Simple. Assuming that you will put this app under `your home folder`/padmonster/:
```Bash
$ git clone https://github.com/jutongpan/padmonster.git ~/padmonster
$ cd ~/padmonster
```

### Testing Gunicorn's Ability to Serve the Project
```Bash
$ gunicorn --bind 0.0.0.0:5000 wsgi:app
```
Visit your server's domain name or IP address with :5000 appended to the end in your web browser: http://server_domain_or_IP:5000. You should be able to access the app up and running.

Now we deactivate the "flask" environment to get back to base.
```Bash
$ conda deactivate
```

### Create a systemd Unit File
```Bash
$ sudo nano /etc/systemd/system/padmonster.service
```

Copy and paste the following in the nano editor:
```
[Unit]
Description=Gunicorn instance to serve padmonster
After=network.target

[Service]
User=jpan
Group=www-data
WorkingDirectory=/home/jpan/padmonster
Environment="PATH=/home/jpan/miniconda3/flask/bin"
ExecStart=/home/jpan/miniconda3/flask/bin/gunicorn --workers 3 --bind unix:padmonster.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
Change all the `jpan` above to your Linux username.
Press `Ctrl` + `X` to exit nano editor, and press `Y` to confirm saving changes before exiting.

We can now start the Gunicorn service we created and enable it so that it starts at boot:
```Bash
$ sudo systemctl start myproject
$ sudo systemctl enable myproject
```

### Configuring Nginx to Proxy Requests
Create a new server block configuration file in Nginx's `sites-available` directory
```Bash
$ sudo nano /etc/nginx/sites-available/padmonster
```

Copy and paste the following in the nano editor:
```
server {
    listen 80;
    server_name server_domain_or_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/jpan/padmonster/padmonster.sock;
    }
}
```
Again change all the `jpan` above to your Linux username. Press `Ctrl` + `X` to exit nano editor, and press `Y` to confirm saving changes before exiting.

To enable the Nginx server block configuration we've just created, link the file to the `sites-enabled` directory:
```Bash
$ sudo ln -s /etc/nginx/sites-available/padmonster /etc/nginx/sites-enabled
```

With the file in that directory, we can test for syntax errors by typing:
```Bash
$ sudo nginx -t
```
If this returns without indicating any issues, we can restart the Nginx process to read the our new config:
```Bash
$ sudo systemctl restart nginx
```

Set up firewall rules to allow for Nginx:
```Bash
$ sudo ufw allow 'Nginx Full'
```

Check whether you can access your app at http://server_domain_or_IP. If so, you are all set.