## CNN-Aided-Factor-Graphs-with-Estimated-Mutual-Information-Features-for-Seizure-Detection-MICAL
#### Bahareh Salafian, Eyal Fishel Ben-Knaan, Nir Shlezinger, Sandrine de Ribaupierre, Nariman Farsad
> We propose a convolutional neural network (CNN) aided factor graphs assisted by mutual information features estimated by a neural network for seizure detection. Specifically, we use neural mutual information estimation to evaluate the correlation between different electroencephalogram (EEG) channels as features. We then use a 1D-CNN to extract extra features from the EEG signals and use both features to estimate the probability of a seizure event. To capture the temporal correlation in the signal, learned factor graphs are employed where both sets of features from the neural mutual estimation and from the 1D-CNN are used to learn the factor nodes. We show that proposed method achieves state-of-the-art performance using 6-fold leave-four-patients out cross validation. 
### Training the Model and Hyperparameters
The number of layers for the proposed 1D CNN are selected same as 2D CNN architecture considered as the baseline model. We also designed the kernel size such that we could get the higher receptive field compared to the prior works. The details for kernel size and layer can be found in our previous paper at: https://arxiv.org/pdf/2108.02372.pdf. 
For training the networks on the CHB-MIT dataset, we use the ADAM optimizer with a learning rate of 0.001, batch size of 256, and 100 epochs of training. The instruction on how to run the codes for training the models are explained at the end of each code in Codes folder in this repository. 

### Tuning the Factor Graph Transitions
In factor graph inference, the transition probabilities are chosen using fine-tuning between the values of 0 and 1 with steps of 0.1. The threshold of 0.5 is used to classify the seizure and no-seizure states during the tuning process.


heloo

