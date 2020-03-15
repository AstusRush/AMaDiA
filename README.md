# AMaDiA
Astus' Mathematical Display Application<br/><br/>
UPDATE: The next update will introduce a lot of fixes as well as a major update to AGeLib. The new AGeLib version changes a lot of internal workings to ensure that future updates are backweards compatible but this takes time. Since the new version also includes the ability so create and save custom colour palettes I don't want to update AMaDiA before the file layout is permanent. In addition to that I had to focus on exams. <br/>What I want to say is: I am still working on AMaDiA weekly (and since corona has caused the exams to be canceled I will now be working daily) and the new version will bring a lot of fixes and improvements and I am sorry that I can't release these improvements in the usual style (which was to release all improvements as soon as they were ready) but I want to ensure that everything is stable and futureproof.<br/>
(Though I wonder to whom I am sorry... I have no idea how many people use AMaDiA... If there is anyone out there who is using AMaDiA feel free to send me any feedback (or even just a "Hey! Cool program!") to a011235robin AT gmail DOT com )<br/><br/>
Current features:<br/>
 * Use (Shift+)AltGr+Key to type Mathematical Symbols (Refer to AMaDiA_ReplacementTables)<br/>
 * Tab 1 : Scientific Calculator<br/>
   * Calculate with +,-,±,×,÷,√,^,°, Integral f(x) dx, d(f(x))/dx, y'(x), complex numbers, sin(), cos(), tan(), exp(), log() , π , E and more<br/>
   * Solve an equation with unknown variables<br/>
   * Solve Differential Equations (including particular solutions)<br/>
   * Test for equality of two terms<br/>
   * Use mathematic Unicode symbols to type faster!<br/>
   * Turn on units in the options to do things like convert_to(7foot+3inch,m)<br/>
   * For more detailed usage check out Help/Examples and copy/paste the examples to the according tab input fields<br/>
 * Tab 2 : Convert input to LaTeX and display it<br/>
 * Tab 3 : Plot 2D Graphs (3D and complex Graphs are WIP)<br/>
 * Tab 4 : Equations with matrices and vectors as well as systems of linear equations<br/>
 * System Control Window : Everything for System Control (WIP)<br/>
 * LAN chat program (needs overhaul)<br/>
   * Intended for sharing equations with other users in the same network to make cooperative working easier<br/>
   * Separate Server and Client applications<br/>
   * Allows sending of text and text files<br/>
   * Share text files with all other users in the network via drag'n'drop into the input field<br/>
   * Server has some moderation tools (Muting/Kicking/Banning<br/>
   * WARNING: Messages are currently not encrypted! Do not send sensitive data!!!<br/>
 * Custom Window Frames<br/>
<br/>
Feedback is welcome<br/>
Suggestions are welcome<br/>
Requests are welcome<br/>
<br/><br/>

# How to Install
On Windows:<br/>
 * Install https://gitforwindows.org/<br/>
 * Install https://www.anaconda.com/distribution/<br/>
 * Create two files "AMaDiA.bat" and "AMaDiA_INSTALL.bat" and copy the text from the two file in WINDOWS-INSTALL into them by rightcklicking on them and selecting the modify option<br/>
 * doubleclick on "AMaDiA_INSTALL.bat" to install AMaDiA (The installation location is the user folder. This can be changed by editing both files.)<br/>
 * From now on doubleclicking on AMaDiA.bat will update and then run AMaDiA<br/>
 
(Disclaimer: Use theses .bat files on your own risk. I doubt they can cause any harm but i am no expert on batch files and can not foresee all eventualities)<br/>
<br/>

   On Linux [WIP]:<br/>
 * sudo apt-install git<br/>
 * Install https://www.anaconda.com/distribution/ or sudo apt-install ...<br/>
 * [Console commands for installation and Alias for Update/Start coming soon(ish?)]<br/>
<br/>

   On OSX [???]:<br/>
 * I don't have access to OSX and am not even sure how good AMaDiA runs on it (it should work flawlessy?)... Sorry but I can not help you...<br/>
 * If anyone has a good description how to easily install/update+run a python script on OSX feel free to inform me so I can add it here<br/>

<br/><br/>
# Screenshot
Screenshot Version 0.15.7.1<br/>
<img src="/AMaDiA v0.15.7.1 Demo.png" alt="Demo Picture"/>
<br/><br/>
# Short Term Roadmap
Planned features for (near) future (order reflects priority):<br/>
- Improve System Control Window<br/>
- Make Tab 4 even easier to use<br/>
- Plot 3D and complex functions<br/>
- (Continuous:) Better parser to allow a more flexible input<br/>
- Simple Texteditor<br/>
- Add more colour-schemes (will be part of the next update including an editor to create and save new ones)<br/>
- better unit handling (like automatic simplification)<br/>
- Automatic recognition for PDEs so that the user no longer has to put them in "pdsolve(...)"<br/>
- PDF-Viewer<br/>
- Save/load the history<br/>
