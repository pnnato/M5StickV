# M5StickV
2020/03/11

This repository is a python code to develop M5StickV camera for interval capturing images.

Function: Button for select date and time manually
Use in: Kochi prefecture farm


Usage Instruction.

1. Click Button B to input date and time
	- The screen refresh showing Year, month, day, hour and minute
	  1. Select month(m) by B button. -> Click A to move to day(d) input 
		-> After "Ok" message pop-up and appear, you can continue to click B button

	  2. Select day(d) by B  button. -> Click A button to move to hour(h) input
		-> After "Ok" message pop-up and appear, you can continue to click B button

	  3. Select hour(h) by B button -> Click A button to move to minute(m) input
		-> After "Ok" message pop-up and appear, you can continue to click B button

	- After finish input, you can start capturing by clicking A button

or 

2. Click Button A to start interval capturing image (every 10 minutes).
	- Wait 10 seconds after clicking
	- Light will turn on before and turn off after taking photo

3. Change date on code (use MaixPy IDE)
Please change at Line 47: now = ..........(refer to epochconverter.com)

- To change year: change at Line 230: get_year = 2020
