PACKAGE TO INSTALL :

car_racing.py:
	- numpy
	- pyglet
	- gym
	- Box2D
	
dqnCustom.py:
	- torch
	- torchvision


python3 record_dataset.py train_set 
python3 record_dataset.py test_set

python3 train.py

python3 drive.py $PWD/models2/model-5.weights

