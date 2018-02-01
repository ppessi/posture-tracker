## Posture Tracker
<p>
A program that will track your posture using a webcam and remind you to sit properly. Works on all operating systems in theory but has only been tested on Linux.
</p>

### Prerequisites
* <a href="https://github.com/cmusatyalab/openface">OpenFace</a> (<a href="http://cmusatyalab.github.io/openface/setup/">Setup instructions for OpenFace</a>)
* The GUI uses Kivy
* Notify-osd needed for notifications at least on Linux systems
* PIL image library
* probably a ton of other stuff, will make an installer or a complete list at some point

### Before usage
* In main.py, in the FaceRecognition class, there is the path to a file. You need to change that to point at the file on your own computer. It can be found in OpenFace's folders.
