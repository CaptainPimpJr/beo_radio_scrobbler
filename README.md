Problem Statement:
When Spotify released Wrapped for the first time, I was beaten in minutes listened to music by far by my friends.  
But, I was actually listening to music on the radio all day long.  
That left me wondering how to track my record of music besides Spotif, since I liked the idea of the analysis of my listening behaviour.  
I had heard of scrobblers but never felt the urge to connect to last.fm.  
Every year every since when a new Wrapped is pubished I have to think again about my "problem".  

Timeline:
When was Wrapped released the first time!? -> Idea was born. Get Radio tracks to Spotify, run the Songs on a headless system...what a waste of energy. 
23rd of Dec. 2025 lying in bed googling stuff...Wrapped is aking me again, since my "musical age" is 66...
And I am again far behind my friends in minutes spend with music, which is unfair, bc I am listening to super good stuff all the time, but it is unrecognized, unrecorded...I am losing street credibility. 
24th of Dec. 2025 starting with some tests while everyone is getting ready for Christmas Eve, working better than expected...
API is understood and workflow is getting artist and title information. 
First scrobble is placed with pylast library. No efforts for me, all the work done by pylast. Time saved. 
25th while the kids are playing with their new toys, scrobbling works with some minor (?) flaws. Code needs to wait here for a second and adding exceptions there is doing the trick. 
Locally my work is done, next step docker, then unraid. 
26th to 30th of Dec 2025. Dockerfile, publishing to Docker Hub, using DHI, getting github actions working propperly, makes me forget how easy the first part was. 

Disclaimer:
This work relies on pylast (https://github.com/pylast/pylast) and uses the BeoNetRemote Client API (https://support.bang-olufsen.com/hc/en-us/articles/360049859212-Drivers-for-3rd-Party-integration & https://documenter.getpostman.com/view/1053298/T1LTe4Lt). I have written the first proof of work using requests and pylast, improved my static if-elese-cases with the help of AI (Claude Sonnet 4.5). Since I have written everything to one main.py, I have asked github copilot to split everything into a modern python project. The Dockerfile is copied and modified from astral/uv official github (https://github.com/astral-sh/uv-docker-example). And I think I will make this readme more fance using github copilot as well. 
