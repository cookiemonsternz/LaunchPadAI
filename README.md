# AI Generated patterns #
A neural network which generates sequences of frames for a launchpad mini mk3.
This uses the launchpads midi ports to send lights to the launmchpad, and a basic sequential neural network for the ai model. 
It was trained on a number of handmade image sequences, which were then augmented to create more variations. This also includes the ability to touch pads on the launchpad and trigger the effects.

https://github.com/user-attachments/assets/e7cc4a81-3244-41cd-aeb4-353ef2d59f4c

### To run locally ###
- Clone the source code
- Make sure you are using Python 3.11 (3.12+ does not work with tensorflow)
- Install required packages
```
pip install mido[ports-rtmidi]
pip install pillow
pip install tensorflow
```
- Run test.py
```
python test.py
```
