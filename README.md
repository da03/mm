# mm

Painful having to enter passwords when copying files among any two machines you have? 

Tired of adding ssh public key files between each pair of machines you have? 

Not able to remember or discriminate the long ip adresses of your machines? 

Machines Management (mm) provides functionalities to manage multiple machines, managing SSH key files automatically for you. You can 

* assign nicknames to your machines, 

* copy files, list files, log in to other machines by using their nicknames, as simple as `mcp nickname1:path/to/file1 nickname2:path/to/file2`.

* avoid entering passwords every time after setting up only ONCE. 

The implementation is purely based on python 2.7, with no additional package requirements.

### Requirements:

You must have a central server with a static ip or domain name in order to maintain the information of other machines. You can only copy files to a machine with a public ip address (or domain name).

### Setup (You only need to do that once for each machine):

Make sure the installation location relative to home directory is the same on every machine.

First, set the central server in `config.txt` such that it has the following format:

```
central: yourusername@youripaddress
```

Make sure the modification of `config.txt` is visible to every machine you want to add. A simple way is to update your github repository and clone it on every machine.

Then central server needs to be set up, on central server do:

```
python setup.py --name central
```

```
source ~/.bashrc
```

On machine1 do the following:

```
python setup.py --name Jacob
```

```
source ~/.bashrc
```

You may be required to enter the password TWICE for your central server. Then the above command will give machine1 a nickname `Jacob`.

On machine2 do the following:

```
python setup.py --name Israel
```

```
source ~/.bashrc
```

This will give machine2 a nickname `Israel`.


### Copy files:

Now, you can copy files using the following command:

```
mcp Jacob/path/to/file1 Israel/path/to/file2
```

Or copy to your local machine (You must run `python setup.py --name nickname` and `source ~/.bashrc` beforehand):

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
