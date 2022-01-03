# Installation

Deployment notes for ramlimit

``` console
$ apt install sudo
$ useradd -m rui
$ usermod -a -G sudo
$ su rui
> cd
> wget -O conda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
...
> chmod u+x conda.sh
> ./conda.sh
...
installing to /home/rui/conda
...
> /home/rui/conda/bin/conda init fish
> conda create -n rui python=3.9
> conda activate rui

# running the backend
> git clone https://github.com/kantholtz/rui-be.git

> mkdir rui-be/lib
> cd rui-be/lib
> git clone https://github.com/kantholtz/ktz.git
> git clone https://git.ramlimit.de/deekpg/draug.git
> git clone https://git.ramlimit.de/deepca/deepca.git
# and install them...

> cd ~/rui-be
> pip install -e .

# set up uwsgi
> conda install -c conda-forge uwsgi
> mkdir data

# test whether it works
> uwsgi --http-socket localhost:5000 --manage-script-name --mount '/=rui_be.app:create_app()'

# as root
> cp /home/rui/rui-be/conf/ramlimit.uwsgi.service /etc/systemd/system/rui.service
> systemctl daemon-reload
> systemctl start rui
> systemctl enable rui

# yet another http server

> apt install nginx
# see /etc/nginx/sites-enabled/default

# frontend:

> cd ~/scm
> git clone https://github.com/kanthotlz/rui-fe.git

> wget -O - https://git.io/fisher | source && fisher install jorgebucaran/fisher
> fisher install jorgebucaran/nvm.fish

> cd ~/scm/rui-fe
> nvm install latest
> npm install
> npm run build
```


* Proxy configuration on `www3`: `/etc/nginx/sites-enabled`
* Certbox configuration enabled for rui: `certbot --nginx`

