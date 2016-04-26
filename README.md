# gg-gpg

#### Progress (Week 4/05)
describe your weekly progress here

#### Progress (Week 3/29)
So far only code done is initial proof of concept of TCP server/ socket which will receive/send gpg encrypted data, respectively.

#### Usage 
See config example file. setup config example file with appropriate values, and run the main.py script with the config file as an argument.
main.py will create a directory structure with each channel's input fifo and output log.
to send to a channel's remote, simply `echo msg > fifo`
to view the output log, `tail out` or any other file viewing command.


#### Getting Started

Requirements: a linux system with the "gpg" command on its path.

prerequisite public and private keys must be downloaded and added to the gpg keyring.


#### Feature implementations  :
* signing messages - a receiver will either see the sender's IP or their uid real name value as the sender based on whether or not the message is signed.
* config file for settings 
* File transfer - implemented with
* separated programs for sender and receiver - each channel can send or receive, or both.
* create fifo file and text output file with messages - each channel has a fifo object and a text output object for what it has received/sent.
