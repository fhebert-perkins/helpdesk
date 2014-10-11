# HelpDesk


Simple helpdesk written in flask whose ticket interface is email. Not entirely meant for production.

*this is by no means done. Use at your own risk*

## Installation


clone the repository

```
git clone https://github.com/fhebert-perkins/helpdesk
```

cd into the directory

```
cd helpdesk
```
create a virtual env and run setup.py this will install the missing requirements

```
virtualenv venv
source venv/bin/activate
python setup.py
```

*for setup.py to work pip must be installed*

to run he webservice run main.py

to run startup mail first edit config.json and then run maildaemon.py

## License (MIT)

Copyright (c) 2012 Finley Hebert-Perkins

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
