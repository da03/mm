# mm

Machines Management provides functionalities to assign nicknames to your machines, and you can copy files, list files, log in to other machines by using their nicknames without having to enter the passwords every time.

### Setup:

First, set the central server in `config.txt` such that it has the following format:

```
central: yourusername@youripaddress
```

Make sure the modification of `config.txt` is visible to every machine you want to add. A simple way is to update your github repository and clone it on every machine.

Then central server needs to be setuped up, on central server do:

```
python setup.py --name central
```

On machine1 do the following:

```
python setup.py --name Jacob
```

You may be required to enter the password TWICE for your central server. Then the above command will give machine1 a nickname `Jacob`.

On machine2 do the following:

```
python setup.py --name Israel
```

This will give machine2 a nickname `Israel`.


### Copy files:

Now, you can copy files using the following command:

```
mcp Jacob/path/to/file1 Israel/path/to/file2
```

Or copy to your local machine (You must run `python setup.py` beforehand):

```
mcp Jacob/path/to/file1 /path/to/file2
```

### Copy directories:

```
mcpr Jacob/path/to/dir1 Israel/path/to/dir2
```

### List files:
Furthermore, you can list files on any machine:

```
mls Jacob/path/to/file1
```

### Log in to other machines:
You can also log in to any machine by nickname:

```
mssh Jacob
```
