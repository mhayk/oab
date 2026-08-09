# The deterministic heart of OAB: same inputs, same numbers, checkable by hand.
Require python3

Output demo/out/calculator.gif
Output demo/out/calculator.webm

Set Width 1080
Set Height 660
Set Padding 24
Set FontSize 15
Set TypingSpeed 30ms
Set WaitTimeout 30s
# Palette source: assets/logo/BRAND.md
Set Theme {"name":"OAB","background":"#0B0F14","foreground":"#E6E6E6","cursor":"#00D1FF","selection":"#232c38","black":"#141A22","red":"#ff6b6b","green":"#3fd08c","yellow":"#e5c07b","blue":"#4aa8ff","magenta":"#b98aff","cyan":"#00D1FF","white":"#E6E6E6","brightBlack":"#5a6674","brightRed":"#ff8f8f","brightGreen":"#6fe0ad","brightYellow":"#f0d49b","brightBlue":"#74bfff","brightMagenta":"#cfaaff","brightCyan":"#2AE7F3","brightWhite":"#FFFFFF"}

Type "cd calculators && python3 -m oab_calc --list"
Sleep 500ms
Enter
Wait
Sleep 3.5s

Type "clear"
Enter

Type "python3 -m oab_calc rps --users=100 --dau-share=0.3 --sessions-per-day=2 --requests-per-session=40 --peak-factor=10"
Sleep 500ms
Enter
Wait
Sleep 9s
