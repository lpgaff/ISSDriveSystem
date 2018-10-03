#!/usr/bin/env python3

import tkinter as tk
import serial
import time
import re
from serial.tools import list_ports
import requests
import urllib3

class Application( tk.Frame ):
	
	# Make frame and all communication handlers
	def __init__( self, master = None ):
		
		# Frame initialisation
		super().__init__( master )
		
		# Position variables
		self.col_label = 0
		self.span_label = 1
		self.col_option = self.col_label + self.span_label
		self.span_option = 3
		self.col_button = self.col_option + self.span_option
		self.span_button = 1
		self.row_port = 0
		self.span_port = 1
		self.row_baud = self.row_port + self.span_port
		self.span_baud = 1
		self.row_parity = self.row_baud + self.span_baud
		self.span_parity = 1
		self.row_bits = self.row_parity + self.span_parity
		self.span_bits = 1
		self.row_datum = self.row_bits + self.span_bits
		self.span_datum = 1
		
		self.row_textentry = self.row_datum + self.span_datum
		self.col_textentry = 0
		self.span_textentry = 3
		
		self.row_axisreturn = self.row_textentry + 1
		self.col_axisreturn = 0
		self.span_axisreturn = 1
		
		self.row_textreturn = self.row_axisreturn
		self.col_textreturn = self.col_axisreturn + self.span_axisreturn
		self.span_textreturn = 3
		
		self.row_connect = 0
		self.span_connect = 2
		self.row_disconnect = self.row_connect + self.span_connect
		self.span_disconnect = 2
		self.row_quit = self.row_disconnect + self.span_disconnect
		self.span_quit = 2
		
		self.row_send = self.row_textentry
		self.col_send = self.col_textentry + self.span_textreturn

		self.row_encoder = 0
		self.col_encoder = self.col_button + self.span_button
		
		# Frame geometry
		self.grid()
		
		# Serial initialisation
		self.serial_port = serial.Serial()
		self.port_open = False
		
		# Selection variables
		self.portalias = tk.StringVar( master )
		self.baudrate = tk.StringVar( master )
		self.parityeven = tk.IntVar()
		self.parityodd = tk.IntVar()
		self.paritynone = tk.IntVar()
		self.parity = tk.IntVar()
		self.bit7on = tk.IntVar()
		self.bit8on = tk.IntVar()
		self.nbits = tk.IntVar()
		self.txt_return = tk.StringVar( master )
		
		# Port option lists
		self.port_opt = list_ports.comports()			# get port list
		self.port_name = {}								# list of devices
		for k in self.port_opt:
			self.port_name[ k.device ] = k.device
		
		# Baudrate option lists
		self.baud_opt = { "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200" }
		
		# Current commands in text box
		self.cmd_now = tk.StringVar( master )
		self.out_now = tk.StringVar( master )
		self.axis_now = tk.StringVar( master )
		
		# Encoder positions and other readouts
		self.encoder_pos = [ 0, 0, 0, 0 ]
		self.enc_disp_txt = []
		for i in range(0,4):
			self.enc_disp_txt.append( tk.StringVar( master ) )
		self.check_enc_status = False

		# Create widgets in an order
		self.do_serial_setup()
		self.create_datum_buttons()
		self.create_text_entry()
		self.create_encoder_display()
		
		# Quit button
		self.quit = tk.Button( self, text="QUIT", fg="red", command=root.destroy )
		self.quit.grid( row=self.row_quit, rowspan=self.span_quit,
					   column=self.col_button, columnspan=self.span_button, sticky="nsew" )
			
		# Set defaults
		self.axis_name = [ 'Trolley', 'Array', 'Target', 'FC' ]
		self.set_defaults()

	# Do serial setup
	def do_serial_setup( self ):
	
		# Set columns and rows
		for x in range(7):
		
			self.rowconfigure( x, weight=2, uniform=1 )
		
		for y in range(6):
			
			self.columnconfigure( y, weight=1, uniform=1 )
	
	
		# Port name menu
		self.portlabel = tk.Label( self, text="Port:" )
		self.portlabel.grid( row=self.row_port, column=self.col_label,
						 rowspan=self.span_port, columnspan=self.span_label, sticky="w" )
		self.port_menu = tk.OptionMenu( self, self.portalias, *self.port_name )
		self.port_menu.grid( row=self.row_port, column=self.col_option,
							rowspan=self.span_port, columnspan=self.span_option, sticky="we" )
			
		# Baud rate menu
		self.baudlabel = tk.Label( self, text="Speed:" )
		self.baudlabel.grid( row=self.row_baud, column=self.col_label,
							rowspan=self.span_baud, columnspan=self.span_label, sticky="w" )
		self.baud_menu = tk.OptionMenu( self, self.baudrate, *self.baud_opt )
		self.baud_menu.grid( row=self.row_baud, column=self.col_option,
							 rowspan=self.span_baud, columnspan=self.span_option, sticky="w" )
			 
		# Parity options
		self.paritylabel = tk.Label( self, text="Parity:")
		self.paritylabel.grid( row=self.row_parity, column=self.col_label,
							 rowspan=self.span_parity, columnspan=self.span_label, sticky="w" )
		self.paritycheckE = tk.Checkbutton( self, text="Even", variable=self.parityeven,
											command=self.seteven, onvalue = 1, offvalue = 0 )
		self.paritycheckO = tk.Checkbutton( self, text="Odd", variable=self.parityodd,
											command=self.setodd, onvalue = 1, offvalue = 0 )
		self.paritycheckN = tk.Checkbutton( self, text="None", variable=self.paritynone,
											command=self.setnone, onvalue = 1, offvalue = 0 )
		self.paritycheckE.grid( row=self.row_parity, column=self.col_option,
								rowspan=self.span_parity, columnspan=1, sticky="w" )
		self.paritycheckO.grid( row=self.row_parity, column=self.col_option+1,
								rowspan=self.span_parity, columnspan=1, sticky="w" )
		self.paritycheckN.grid( row=self.row_parity, column=self.col_option+2,
								rowspan=self.span_parity, columnspan=1, sticky="w" )
			 
			 
			 
		# Bits menu
		self.bitslabel = tk.Label( self, text="Bits:" )
		self.bitslabel.grid( row=self.row_bits, column=self.col_label,
						  rowspan=self.span_bits, columnspan=self.span_label, sticky="w" )
		self.bits7 = tk.Checkbutton( self, text="7", variable=self.bit7on, command=self.set7 )
		self.bits8 = tk.Checkbutton( self, text="8", variable=self.bit8on, command=self.set8 )
		self.bits7.grid( row=self.row_bits, column=self.col_option,
							rowspan=self.span_bits, columnspan=1, sticky="w" )
		self.bits8.grid( row=self.row_bits, column=self.col_option+1,
							rowspan=self.span_bits, columnspan=1, sticky="w" )
								 
		# Connect button
		self.connect = tk.Button( self, text="CONNECT", fg="green", command=self.connect_to_port )
		self.connect.grid( row=self.row_connect, rowspan=self.span_connect,
						   column=self.col_button, columnspan=self.span_button, sticky="nsew" )
													 
		# Disconnect button
		self.disconnect = tk.Button( self, text="DISCONNECT", fg="red", command=self.disconnect_port )
		self.disconnect.grid( row=self.row_disconnect, rowspan=self.span_disconnect,
								column=self.col_button, columnspan=self.span_button, sticky="nsew" )


	# Create buttons
	def create_datum_buttons( self ):

		# Datum entries	
		self.datum_button = []

		# Datum search 1
		self.datum_button.append(
				tk.Button( self, text="Datum 1", fg="purple", command=lambda:self.datum_search(1) )	)
		self.datum_button[0].grid( row=self.row_datum, column=0, sticky="nsew" )	
	
		# Datum search 2
		self.datum_button.append(
				tk.Button( self, text="Datum 2", fg="purple", command=lambda:self.datum_search(2) )	)
		self.datum_button[1].grid( row=self.row_datum, column=1, sticky="nsew" )	
	
		# Datum search 3
		self.datum_button.append(
				tk.Button( self, text="Datum 3", fg="purple", command=lambda:self.datum_search(3) )	)
		self.datum_button[2].grid( row=self.row_datum, column=2, sticky="nsew" )	
	
		# Datum search 4
		self.datum_button.append(
				tk.Button( self, text="Datum 4", fg="purple", command=lambda:self.datum_search(4) )	)
		self.datum_button[3].grid( row=self.row_datum, column=3, sticky="nsew" )	
	
	# Create text entry manual commands
	def create_text_entry( self ):
		
		# Command
		self.txtcmd = tk.Entry( self, textvariable=self.cmd_now )
		self.txtcmd.grid( row=self.row_textentry, column=self.col_textentry,
						 rowspan=1, columnspan=self.span_textentry,
						 sticky="nsew" )
		self.txtcmd.bind( '<Return>', self.writers232 )
		
		# Axis
		self.axisout = tk.Entry( self, textvariable=self.axis_now )
		self.axisout.grid( row=self.row_axisreturn, column=self.col_axisreturn,
						  rowspan=1, columnspan=self.span_axisreturn,
						  sticky="nsew" )		

		# Return
		self.txtout = tk.Entry( self, textvariable=self.out_now )
		self.txtout.grid( row=self.row_textreturn, column=self.col_textreturn,
						  rowspan=1, columnspan=self.span_textreturn,
						  sticky="nsew" )
		
		# Send button
		self.sendbutton = tk.Button( self, text="Send", fg="green", command=self.writers232 )
		self.sendbutton.grid( row=self.row_send, rowspan=1,
							  column=self.col_send, columnspan=1,
							  sticky="nsew" )

	# Create encoder readout display
	def create_encoder_display( self ):
		
		# Encoder button
		self.enc_button = tk.Button( self, text="Check positions", fg="blue",
										command=self.check_encoder_pos )
		self.enc_button.grid( row=self.row_encoder, column=self.col_encoder, sticky="nsew" )

		# Encoder entries
		self.enc_disp = []

		# Encoder 1
		self.enc_disp.append( tk.Entry( self, textvariable=self.enc_disp_txt[0] ) )
		self.enc_disp[0].grid( row=self.row_encoder+1, column=self.col_encoder, sticky="nsew" )

		# Encoder 2
		self.enc_disp.append( tk.Entry( self, textvariable=self.enc_disp_txt[1] ) )
		self.enc_disp[1].grid( row=self.row_encoder+2, column=self.col_encoder, sticky="nsew" )

		# Encoder 3
		self.enc_disp.append( tk.Entry( self, textvariable=self.enc_disp_txt[2] ) )
		self.enc_disp[2].grid( row=self.row_encoder+3, column=self.col_encoder, sticky="nsew" )

		# Encoder 4
		self.enc_disp.append( tk.Entry( self, textvariable=self.enc_disp_txt[3] ) )
		self.enc_disp[3].grid( row=self.row_encoder+4, column=self.col_encoder, sticky="nsew" )


	###########
	# Actions #
	###########

	# set the parity to even
	def seteven( self ):
	
		self.parity.set(serial.PARITY_EVEN)
		self.parityodd.set(0)
		self.parityeven.set(1)
		self.paritynone.set(0)
	
	# set the parity to odd
	def setodd( self ):
		
		self.parity.set(serial.PARITY_ODD)
		self.parityodd.set(1)
		self.parityeven.set(0)
		self.paritynone.set(0)
	
	# set the parity to none
	def setnone( self ):
		
		self.parity.set(serial.PARITY_NONE)
		self.parityodd.set(0)
		self.parityeven.set(0)
		self.paritynone.set(1)
	
	# set the number of bits to 7
	def set7( self ):
		
		self.nbits.set(serial.SEVENBITS)
		self.bit7on.set(1)
		self.bit8on.set(0)
	
	# set the number of bits to 8
	def set8( self ):
		
		self.nbits.set(serial.EIGHTBITS)
		self.bit7on.set(0)
		self.bit8on.set(1)
	
	# Create serial port
	def connect_to_port( self ):
		
		self.serial_port.port = self.portalias.get()			# set name of port
		self.serial_port.baudrate = int( self.baudrate.get() )	# set baud rate
		self.serial_port.parity = serial.PARITY_EVEN			# set parity
		self.serial_port.bytesize = serial.SEVENBITS			# set bytesize
		self.serial_port.timeout = 3							# set timeout to 3 seconds
		self.serial_port.open()									# open the port
		
		if self.serial_port.is_open == True:
			
			tmpStr = "Connected to " + self.portalias.get()
			self.out_now.set( tmpStr )
			print( tmpStr )
	
		else:
		
			tmpStr = "Failed to connect to " + self.portalias.get()
			self.out_now.set( tmpStr )
			print( tmpStr )

	# Disconnect from serial port
	def disconnect_port( self ):
		
		self.serial_port.close()	# close the port
		self.out_now.set( "Disconnected" )
		print( "Disconnected" )

	# go to position 1
	def select_pos( self, pos ):
		
		print( "moving to position", pos )
	

	# datum search
	def datum_search( self, axis ):
		
		print( "Datum search on axis", axis )
		
		# Set acceleration
		in_cmd = ( str(axis) + 'sa500\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Set deceleration
		in_cmd = ( str(axis) + 'sd1000\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Set velocity
		in_cmd = ( str(axis) + 'sv1000\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Set creep
		in_cmd = ( str(axis) + 'sc200\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Set datum mode
		in_cmd = ( str(axis) + 'dm00101000\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Go home to datum
		in_cmd = ( str(axis) + 'hd\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)

		# Check position
		self.check_encoder_pos_axis(axis)

		# Display current operation
		in_cmd = ( str(axis) + 'co\r' ).encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		time.sleep(0.1)
	
		# Check position
		self.check_encoder_pos_axis(axis)

	# write info
	def writers232( self, event=None ):
	
		in_cmd = (self.cmd_now.get()+'\r').encode()
		print( in_cmd )
		self.serial_port.write( in_cmd )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		print( outputline )
		outputline.decode('utf8')
		pattern = re.match(b'.*\\r(\d*):(.*)\\r\\n', outputline, re.IGNORECASE)

		if pattern is not None:
			self.axis_now.set( pattern.group(1) )
			self.out_now.set( pattern.group(2) )
	
		self.check_encoder_pos()

	# check encoder positions
	def check_encoder_pos( self ):

		self.check_encoder_pos_axis(1)
		self.check_encoder_pos_axis(2)
		self.check_encoder_pos_axis(3)
		self.check_encoder_pos_axis(4)

	# check encoder positions
	def check_encoder_pos_axis( self, axis ):

		in_cmd = ( '%doa\r' % axis ).encode()
		self.serial_port.write( bytes(in_cmd) )
		time.sleep(0.1)
		outputline = self.serial_port.readline()
		outputline.decode('utf8')
		#outputline = "3oa\\r03:0\\r\\n"
		print( outputline )
		pattern = re.match(b'.*\\r(\d*):(-?\d*).*\\r\\n', outputline, re.IGNORECASE)
		#print( pattern )

		if pattern is not None:
			self.encoder_pos[axis-1] = int( pattern.group(2) )
			self.enc_disp_txt[axis-1].set( ('%d: %d' % ( axis, int( pattern.group(2) ) ) ) )
			self.send_to_influx( axis, int( pattern.group(2) ) )

	# send positions to InfluxDB
	def send_to_influx( self, axis, pos ):

		payload = 'encoder,axis=' + str(axis) + ',name=' + str(self.axis_name[axis-1]) + ' value=' + str(pos)
		r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=positions', data=payload, auth=("admin","issmonitor"), verify=False )
		

	
	############
	# Defaults #
	############
	
	def set_defaults( self ):
		
		self.seteven()
		self.set7()
		self.baudrate.set( "9600" ) # initial value
		self.portalias.set( self.port_opt[0].device )	# initial value


##################
# Main programme #
##################

urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
root = tk.Tk()
app = Application( master = root )
app.mainloop()
