import os
import wx

# replace line 22
REMOVELEVEL = "; REMOVED: < M420 S0 > which disabled the leveling matrix \n"

# replace lines 27-43
QUICKPRINT = "M117 Preparing NO leveling...; Let the user know we're on it \n\
G1 E-1 F100 ; retract filament \n\
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


	def OnOpen(self):

		# ask the user what new file to open
		with wx.FileDialog(self, 
							message="Open gcode file", 
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
			

	def makeFast(self, fileobj):
		# output name. TODO take in as optional param at run, check it's not already '_fast'
		outpath = self.pathname.replace(".gcode", "_fast.gcode")
		with open(outpath, "w") as outfile:
			for row,line in enumerate(fileobj):
				# Comment out line 22: M420 SO ; which disables the previous leveling info so we can rapid starting
				if row == 21:
					outfile.write(REMOVELEVEL)
				elif row >= 26 and row <= 41:
					# do nothing because we're replacing those lines
					continue
				# Write out new info from lines 27 - 43
				elif row == 42:
					outfile.write(QUICKPRINT)
					# we're now at line 37 after writing all that
				# Write out fast print message at line 47
				elif row == 46:
					outfile.write(NEWMESSAGE)
				# For all the lines we're not replacing, keep them the same
				else:
					outfile.write(line)
		
		with wx.MessageDialog(parent=None, 
								message=f"Done! File successfully saved to: {outpath}",
								caption="Success",
								style=wx.OK|wx.ICON_INFORMATION) as msg:
				msg.ShowModal()
		self.Close()
	
	
if __name__ == "__main__":
	app = wx.App(False)
	win = Fastify()
	win.OnOpen()
	app.MainLoop()
	
			