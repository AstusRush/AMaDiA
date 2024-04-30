# AMaDiA
Astus' Mathematical Display Application<br/><br/>
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
 * Here https://github.com/AstusRush/AMaDiA/issues/2 is a description by someone who installed it on OSX

<br/><br/>
# Screenshot
Screenshot Version 0.15.7.1<br/>
<img src="/AMaDiA v0.15.7.1 Demo.png" alt="Demo Picture"/>
<br/><br/>
# "Short" Term Roadmap
Planned features for near future (order reflects priority) (note that the word "short" is very relative here):<br/>
- Plot 3D and complex functions<br/>
- Improve System Control Window<br/>
- (Continuous:) Better parser to allow a more flexible input<br/>
<br/><br/>
# Long Term Roadmap
Planned features for future (order reflects priority):<br/>
- Make Tab 4 even easier to use<br/>
- Simple Texteditor<br/>
- better unit handling (like automatic simplification)<br/>
- Automatic recognition for PDEs so that the user no longer has to put them in "pdsolve(...)"<br/>
- Save/load the history<br/>
- PDF-Viewer<br/>
