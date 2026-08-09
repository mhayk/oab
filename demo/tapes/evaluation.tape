# The proof: five scenarios guarding both failure directions, perturbed 100x and 0.01x to
# confirm they respond to magnitude rather than recognising specific numbers.
# demo/render.sh creates .venv with the dev dependencies first.
Require python3

Output demo/out/evaluation.gif

Set Width 1080
Set Height 460
Set Padding 24
Set FontSize 15
Set TypingSpeed 30ms
Set WaitTimeout 60s
# Palette source: assets/logo/BRAND.md
Set Theme {"name":"OAB","background":"#0B0F14","foreground":"#E6E6E6","cursor":"#00D1FF","selection":"#232c38","black":"#141A22","red":"#ff6b6b","green":"#3fd08c","yellow":"#e5c07b","blue":"#4aa8ff","magenta":"#b98aff","cyan":"#00D1FF","white":"#E6E6E6","brightBlack":"#5a6674","brightRed":"#ff8f8f","brightGreen":"#6fe0ad","brightYellow":"#f0d49b","brightBlue":"#74bfff","brightMagenta":"#cfaaff","brightCyan":"#2AE7F3","brightWhite":"#FFFFFF"}

Type ".venv/bin/python evaluations/runner/run_scenarios.py --perturb"
Sleep 500ms
Enter
Wait
Sleep 7s
