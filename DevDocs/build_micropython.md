
# Building MicroPython

Whilst testing the clock with H:M:S display, I found that the martian time wasn't updating.
Testing the code in python3.10, everything worked fine.
I think it comes down to the float precision, MicroPython uses single precision floats by default whist python proper uses double.
This can be changed when uP is built, documentation here is how I did it.


## Contents
* Setup:
  * Update and accept agreements for Xcode (not documented here)
  * [Arm Compiler](#arm-compiler)
  * [Install MacPorts](#install-macports)
* [Build MicroPython](#build-microPython)


## Setup

See: https://github.com/micropython/micropython/wiki/Getting-Started#mac-osx

### Arm compiler
**TLDR:** `brew install --cask gcc-arm-embedded`

Triggered the following error when running `cd micropython/ports/rp2double/build ; cmake ..`

```
PICO_SDK_PATH is []/micropython/lib/pico-sdk
PICO platform is rp2040.
CMake Error at []/micropython/lib/pico-sdk/cmake/preload/toolchains/find_compiler.cmake:28 (message):
  Compiler 'arm-none-eabi-gcc' not found, you can specify search path with
  "PICO_TOOLCHAIN_PATH".
Call Stack (most recent call first):
  []/micropython/lib/pico-sdk/cmake/preload/toolchains/pico_arm_gcc.cmake:20 (pico_find_compiler)
  /usr/local/Cellar/cmake/3.27.7/share/cmake/Modules/CMakeDetermineSystem.cmake:148 (include)
  CMakeLists.txt:76 (project)
```

This thread gives a solution: https://stackoverflow.com/questions/59861085/how-to-install-gcc-arm-none-eabi-at-mojave-macos
```
brew install armmbed/formulae/arm-none-eabi-gcc
```
Based on the comments, I went with this instead:
```
brew install --cask gcc-arm-embedded
```


### Install MacPorts

Based on this, but also I think it's out of date: https://github.com/micropython/micropython/wiki/Micro-Python-on-Mac-OSX
```
# libffi (minimum version 3.1-4 from Macports)
sudo port install libffi
#pkgconfig
sudo port install pkgconfig
```

## Build MicroPython

Based on docs at:
* https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf
* https://forums.raspberrypi.com/viewtopic.php?t=319525
* https://community.element14.com/products/raspberry-pi/b/blog/posts/pi-pico-rp2040-micropython-double-precision
* https://forum.micropython.org/viewtopic.php?t=9965


Clone the directory, switch to a tagged version, install submodules
```
mkdir -p ~/Projects/Code/micropython/srccode_v1_21/
git clone https://github.com/micropython/micropython.git
cd micropython
git checkout tags/v1.21.0
git submodule update --init
```

I'm not sure why I did this - I think it's for building a unix version that I don't need
```
cd micropython/ports/unix
make submodules
make deplibs
```
This last step fails `make axtls`

Setup something?
```
cd micropython
make -C mpy-cross
```

Make a double precision version for pico
```
cd micropython/ports
cp -r ports/rp2 ports/rp2double

make -C ports/rp2double submodules

# vi ports/rp2double/mpconfigport.h
# replace:
# >> #define MICROPY_FLOAT_IMPL                      (MICROPY_FLOAT_IMPL_FLOAT)
# with:
# << #define MICROPY_FLOAT_IMPL                      (MICROPY_FLOAT_IMPL_DOUBLE)

rm -rf ports/rp2double/build
mkdir ports/rp2double/build
cd ports/rp2double/build

cmake ..
make
```

I also saw this but never ran it:
```
  cd micropython/ports/rp2
  make -j4
  picotool info -a build/firmware.uf2
```

It seems to have worked:
```
$ picotool info -a firmware.uf2
File firmware.uf2:

Program Information
 name:            MicroPython
 version:         v1.21.0
 features:        thread support
                  USB REPL
 frozen modules:  neopixel, dht, ds18x20, onewire, uasyncio, asyncio/stream, asyncio/lock, asyncio/funcs, asyncio/event, asyncio/core, asyncio, _boot,
                  rp2, _boot_fat
 binary start:    0x10000000
 binary end:      0x1004f3e0
 embedded drive:  0x100a0000-0x10200000 (1408K): MicroPython

Fixed Pin Information
 none

Build Information
 sdk version:       1.5.1
 pico_board:        pico
 boot2_name:        boot2_w25q080
 build date:        Dec 15 2023
 build attributes:  MinSizeRel
```

Install onto the pico:
https://micropython.org/download/RPI_PICO/
```
cp ./firmware.uf2  /Volumes/RPI-RP2/
```
