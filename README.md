# CNN-Aided-Factor-Graphs-with-Estimated-Mutual-Information-Features-for-Seizure-Detection-MICAL
The number of layers for the proposed 1D CNN are selected same as 2D CNN architecture considered as the baseline model. We also designed the kernel size such that we could get the higher receptive field compared to the prior works. The details for kernel size and layer can be found in our previous paper at: https://arxiv.org/pdf/2108.02372.pdf

For training the networks on the CHB-MIT dataset, we use the ADAM optimizer with a learning rate of 0.001, batch size of 256, and 100 epochs of training. The instruction on how to run the codes for training the models are explained at the end of each code in Codes folder in this repository. 

In factor graph inference, the transition probabilities are chosen using fine-tuning between the values of 0 and 1 with steps of 0.1. Also, the threshold of 0.5 is used to classify the seizure and no-seizure states. 




