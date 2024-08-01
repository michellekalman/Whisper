# Whisper
I supported all the features including the bonuses.
How to test the project?
I have two configurations- one for an http target server and one for a tcp target server.
to test the flow we need to run the wanted server, then run the whisper file and then run the wanted clients- I created two regular clients and one client that sends the destruct message.
How whisper operates?
Whisper waits for connentions while using ThreadPoolExecutor to handle multiple concurrent connections.
For each connection I recieve the data from the client, decrypt it and create the header.
I check the data for the destruct msg:
  If it is the destruct msg, I trigger the destruction event and destruct as requested.
  If not, I create the enriched data that contains the header and the data, encrypt it and transfer the enriched data according to the server type
