# Real installation, really executed — demo/render.sh removes the marketplace first so the
# add and install below genuinely run rather than reporting "already installed".
Require claude

Output demo/out/install.gif

Set Width 960
Set Height 300
Set Padding 24
Set FontSize 15
Set TypingSpeed 35ms
Set WaitTimeout 120s
# Palette source: assets/logo/BRAND.md
Set Theme {"name":"OAB","background":"#0B0F14","foreground":"#E6E6E6","cursor":"#00D1FF","selection":"#232c38","black":"#141A22","red":"#ff6b6b","green":"#3fd08c","yellow":"#e5c07b","blue":"#4aa8ff","magenta":"#b98aff","cyan":"#00D1FF","white":"#E6E6E6","brightBlack":"#5a6674","brightRed":"#ff8f8f","brightGreen":"#6fe0ad","brightYellow":"#f0d49b","brightBlue":"#74bfff","brightMagenta":"#cfaaff","brightCyan":"#2AE7F3","brightWhite":"#FFFFFF"}

Type "claude plugin marketplace add mhayk/oab"
Sleep 500ms
Enter
Wait
Sleep 1.5s

Type "claude plugin install oab@oab"
Sleep 500ms
Enter
Wait
Sleep 3s
