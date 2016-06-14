# mm

## Usage:

First, set the central server in `config.txt` such that it has the following format:

```
central: yourusername@youripaddress
```

Make sure the modification of `config.txt` is visible to every machine you want to add. A simple way is to update your github repository and clone it on every machine.

On machine1 do the following:

```
python setup.py --name Jacob
```

You may be required to enter the password for your central server. Then the above command will give machine1 a nickname `Jacob`.

On machine2 do the following:

```
python setup.py --name Israel
```

This will give machine2 a nickname `Israel`.

Afterwards, you can copy files using the following command:

```
mcp Jacob/path/to/file1 Israel/path/to/file2
```

Or copy to your local machine (You must run `python setup.py` beforehand):

```
mcp Jacob/path/to/file1 /path/to/file2
```

Furthermore, you can list files on any machine:

```
mls Jacob/path/to/file1
```
