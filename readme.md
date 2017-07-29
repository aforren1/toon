Create environment:

```
conda create --name toon python==3.6
activate toon
conda install numpy scipy
pip install git+https://github.com/psychopy/psychopy
pip install keyboard nidaqmx pyusb hidapi
conda install -c m-labs libusb 
```
