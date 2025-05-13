# openlab2025

rocky lab team1

## setup

You need webcam to use this app.

You need pygame, cv2, mediapipe.

```
% pip install pygame
```

```
% pip install computer-vision
```

```
% pip install mediapipe
```

## how to use

```
python shooting_game.py
```

You can use 3 hand poses, and "player" follows your index finger.

Poses are "pinch", "pointing" and "open-hand".

<!-- ![pinch](images/body_finger_ok.png) -->
<!-- ![pointing](images/pose_hitosashiyubi.png) -->
<!-- ![openhand](images/virus_hand_clean.png) -->
<img src="images/body_finger_ok.png" width="20%">
<img src="images/pose_hitosashiyubi.png" width="15%">
<img src="images/virus_hand_clean.png" width="20%">

### start menu

Pinch to start.

### game started

Erase enemys, the score will increase.

Pointing to shot.

Open-hand to barrier.

### game over / game clear

Pinch to restart.
