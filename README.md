i38
============

i38 is an implementation of a Reddit / Hacker News style news web site written using Python, Cherrypy and MySQL


# Create python virtual environment

```
$ sudo pip install virtualenv
```

OR 

```
$ sudo apt-get install python-virtualenv
```

Create virtual environment

```
$ mkdir myproject
$ cd myproject
$ virtualenv venv
New python executable in venv/bin/python
Installing distribute............done.
```

# Active virtual environment

```
$ . venv/bin/activate
```

# Start MySQL on OSX

```
sudo /usr/local/bin/mysql.server start
```

# Launch i38

```
cd /i38/src/i38
python root.py
```

