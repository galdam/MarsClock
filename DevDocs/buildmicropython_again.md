```
    brew install --cask docker virtualbox 
    brew install docker-machine
    docker-machine create --driver virtualbox default
    docker-machine restart
    eval "$(docker-machine env default)" # This might throw an TSI connection error. In that case run docker-machine regenerate-certs default
    (docker-machine restart) # maybe needed
    docker run hello-world

```

https://apple.stackexchange.com/questions/373888/how-do-i-start-the-docker-daemon-on-macos
https://spiffyeight77.com/posts/all/2024/11/replacing-docker-desktop-on-macos-with-lima/
```
brew install lima docker

brew install lima-additional-guestagents
limactl create --name=docker \
  --arch=x86_64 \
  --cpus=1 \
  --memory=2 \
  --disk=20 \
  --vm-type=vz \
  --mount-type=virtiofs \
  --mount=$HOME:w \
  template://docker

limactl start docker

docker context create lima-docker --docker "host=unix:///Users/gabe/.lima/docker/sock/docker.sock"
docker context use lima-docker
docker run hello-world

docker context create lima-docker --docker "host=unix://${HOME}/.lima/docker/sock/docker.sock"
docker context use lima-docker

# you are done:
docker run --rm hello-world

```


```
docker run --mount type=bind,src=/Users/gabe/Projects/micropython,dst=/micropython -it micropython/build-micropython-arm sh
```

```
mkdir -p /micropython/srccode_v1_26_1/
git clone https://github.com/micropython/micropython.git
cd micropython
git checkout tags/v1.26.1
git submodule update --init

make -C mpy-cross clean
make -C mpy-cross


cp -r ports/rp2 ports/rp2double

grep MICROPY_FLOAT_IMPL_FLOAT ports/rp2double/mpconfigport.h
grep MICROPY_FLOAT_IMPL_DOUBLE ports/rp2double/mpconfigport.h

sed -i 's/MICROPY_FLOAT_IMPL_FLOAT/MICROPY_FLOAT_IMPL_DOUBLE/g' ports/rp2double/mpconfigport.h

make -C ports/rp2double submodules

cd
make -C ports/rp2double submodules all BOARD=RPI_PICO2_W

cd ports/rp2double/build-RPI_PICO2_W
picotool info -a firmware.uf2


export PICO_SDK_PATH=/micropython/pico/pico-sdk