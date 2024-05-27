# Introduction 
A custom application to record multichannel lossless audio and tracking data synchronously. Tracking is realized with the Atracsys System [Fusion Track 500](https://www.atracsys-measurement.com/products/fusiontrack-500/). 

# VAT CAPTURE
The application is designed to navigate previously planned pedicle screw drillings using a drill sleeve. The main window constitutes of three separate views of the current vertebra: the posterior view, the axial view and the sagital view.
![VAT Capture](assets\vat-capture.PNG)

## Configurations
The program runs on different configuration files. [capture-default.yaml](configs\capture-default.yaml) defines the standard run configurations, such as *time_filter*, *stats_timeout*, *markers*, *geometries* and statistics.

[defaults.yaml](configs\defaults.yaml) defines default properties of any kind. Anything that is defined as defined as default in this file, does not have to be defined again. Currently, default *geometries* are defined.

[pilot-faros.yaml](configs\pilot-faros.yaml) defines a sample configuration for a lumbar spine surgery. Replace or modify this file to define your custom configuration.

## Undetected Markers
If an anticipated marker is not detected, all its corresponding geometries are not visualized until they appear. The same happens if a marker has not been detected for *time_filter* milliseconds. This parameter can be adjusted in [capture-default.yaml](configs\capture-default.yaml).

## Interactions

| **interaction** | **explanation** |
| --- | --- |
| **mouse** | Holding the left mouse button and moving in the 3d viewer results in orbiting the vertebra's center of gravity |
| **shift + mouse** | Holding the left mouse button and the shift key while moving in the 3d viewer results in rotating the vertebra around the viewing axis. Only up and down mouse movements are taking into consideration. |
| **keys** | Use the up, down, left and right key to orbit the vertebra's center of gravity |


## Buttons & Combo Boxes

| **button** | **explanation** |
| - | - |
| **recording** | The record button changes between *START RECORDING* and *STOP RECORDING* depending whether the poses are currently being recorded. Recordings are saved to the folder [data-tracking](/data-tracking) in a csv format consisting of marker id, timestamp, position and rotation. |
| **synchronization** | The *SYNC* button synchronizes changes to the camera position of the different views. Once pressed, the views can be individually manipulated. Upon pressing the button again, the views are once again synchronized. |
| **Vertebra** | The text on this button depends on the experiment configuration file, for example *L1 - left*. You can switch between all the different experiment configurations you have defined. |
| **Navigation Method** | You can switch between *Entry Point* and *Screw Tip* Navigation methods. While the *entry point* navigatio method focuses on finding an entry point and following the planned trajectory, the *screw tip* navigation method lets you choose the entry point yourself and guides you towards the planned screw tip.


# VAT AUDIO
The application is designed to visualize the incoming audio signal.
![VAT Capture](assets\vat-audio.PNG)

## Configurations
The program runs on a configuration file. [audio-default.yaml](configs\audio-default.yaml) defines the standard run configurations, such as *chunk_size*, *fps*, *input_device*, *input_channels* and the number of displayed frames.


# Step by Step
1. Clone the repository
```bash
git clone https://caspa.visualstudio.com/Machine%20Learning/_git/vat-capture
```
1. Initialize and activate your favorite python environment (virtualenv: `python -m venv {venv}` or conda)
2. For live viewing atracsys data: setup atracsys sdk (see document in MS Teams -> ROCS -> atracsys fusiontack 500 -> files -> internal manual -> setup) **AND** add the system variables as in the [documentation](https://pypi.org/project/atracsys/) ATRACSYS_FTK_HOME & ATRACSYS_STK_HOME to something like "documents/.../fusionTrack SDK x64"
3. Install all packages from [requirements.txt](requirements.txt) or [requirements-by-hand.txt](requirements-by-hand.txt) `pip install -r requirements.txt`
4. Run the code. Feel free to create your own configuration files or change the default one.
```Python
python vat-capture.py configs/pilot-faros.yaml
python vat-audio.py configs/audio-default.yaml
```

# Contributors
This repository is a collaboration between Aidana Massalimova and Severin Pfister.
