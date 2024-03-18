import os
import wx

# replace line 22
REMOVELEVEL = "; REMOVED: < M420 S0 > which disabled the leveling matrix \n"

## Shoutout to Lulzbot forum user b-morgan for inspiring the mods. Tweaked from his example and Z offsets changed.
## Sauce: https://forum.lulzbot.com/t/taz-quickstart-skip-leveling-wipe/7046/6
# replace lines 27-43
QUICKPRINT = "M117 Preparing NO leveling...; Let the user know we're on it \n\
G1 E-2 F100 ; retract filament \n\
G28 XY ; home X and Y \n\
G1 X-19 Y258 F1000 ; move to safe homing position \n\
G28 Z ; home Z \n\
G1 Z10 ; raise extruder to clear any obstacles \n\
G92 Z8.5; apply z-offset \n\
G1 X0 Y0 F5000 ; move to starting point \n\
M117 Heating... ; progress indicator on LCD \n"

# replace line 47
NEWMESSAGE = "M117 TAZ6 Fast Printing... ; progress indicator message on LCD \n"

class Fastify(wx.Frame):
	""" Overwrites the leveling and wiping sequence in gcode from Cura
		Lulzbot Edition Version 3.6.x. Tested on Ver 3.6.40.
	"""
	
	def __init__(self):
		wx.Frame.__init__(self, 
							None, 
							wx.ID_ANY, 
							"Make Taz6 gcode fast")
		self.cwd = os.getcwd()


	def onOpen(self):
		# ask the user what new file to open
		with wx.FileDialog(self, 
							message="Open gcode File to Make Fast", 
							defaultDir=self.cwd,
							wildcard="gcode files (*.gcode)|*.gcode",
							style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				self.Close()	 # the user changed their mind
				return

			# Proceed loading the file chosen by the user
			pathname = fileDialog.GetPath()
			# save to class for later manipulation
			self.pathname = pathname
			try:
				with open(pathname, 'r') as file:
					self.makeFast(file)
			except IOError:
				wx.LogError("Cannot open file '%s'." % newfile)
			

	def makeFast(self, readfrom):
		# output name. TODO give user choice of output filename
		defaultpath = self.pathname.replace(".gcode", "_fast.gcode")
		# Give user a saveas file dialog for new file:
		with wx.FileDialog(self,
							message="Save Fast gcode As...",
							defaultDir=self.cwd,
							defaultFile=os.path.splitext(os.path.basename(defaultpath))[0],
							wildcard="gcode files (*.gcode)|*.gcode",
							style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as saveas:
							
			if saveas.ShowModal() == wx.ID_CANCEL:
				self.Close()		# User changed their mind
				return
			outpath = saveas.GetPath()
			
			try:
				with open(outpath, 'w') as saveto:
					self.writeFile(readfrom, saveto)
			except IOError:
				wx.LogError("Cannot write to file '%s'." % outpath)
		
		
		with wx.MessageDialog(parent=None, 
								message=f"Done! File successfully saved to: {outpath}",
								caption="Success",
								style=wx.OK|wx.ICON_INFORMATION) as msg:
				msg.ShowModal()
		self.Close()
	
	def writeFile(self, original, faster):
		""" Takes in two file objects to write out new faster gcode.
		"""

		for row,line in enumerate(original):
			# Comment out previous line 22: M420 SO ; which disables the previous leveling info so we can rapid start
			if row == 21:
				faster.write(REMOVELEVEL)
			elif row >= 26 and row <= 41:
				# do nothing because we're replacing those lines
				continue
			# Write out new info from previous lines 27 - 43 to skip bed level and wipe
			# QUICKPRINT simplifies setup and just homes axes, hovers 10mm Z, retracts filament, and heats up.
			elif row == 42:
				faster.write(QUICKPRINT)
				# new file will be at line 36 after writing all that
			# Write out fast print message at previous line 47
			elif row == 46:
				faster.write(NEWMESSAGE)
			# For all the lines we're not replacing, keep them the same
			else:
				faster.write(line)

	
if __name__ == "__main__":
	app = wx.App(False)
	win = Fastify()
	win.onOpen()
	app.MainLoop()
	
	