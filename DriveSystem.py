#!/usr/bin/env python3

import tkinter as tk
import serial
from serial.tools import list_ports

class Application( tk.Frame ):
	
	# Make frame and all communication handlers
	def __init__( self, master = None ):
		
		# Frame initialisation
		super().__init__( master )
		
		# Position variables
		self.col_label = 0
		self.span_label = 1
		self.col_option = self.col_label + self.span_label
		self.span_option = 6
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
		self.row_target = self.row_bits + self.span_bits
		self.span_target = 1
		
		self.row_connect = 0
		self.span_connect = 2
		self.row_disconnect = self.row_connect + self.span_connect
		self.span_disconnect = 2
		self.row_quit = self.row_disconnect + self.span_disconnect
		self.span_quit = 2
		
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
		self.parity = tk.StringVar()
		self.nbits = tk.StringVar()
		
		# Port option lists
		self.port_opt = list_ports.comports()			# get port list
		self.port_name = {}								# list of devices
		for k in self.port_opt:
			self.port_name[ k.device ] = k.device
		
		# Baudrate option lists
		self.baud_opt = { "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200" }
		
		# Create widgets in an order
		self.do_serial_setup()
		self.create_target_buttons()

		# Quit button
		self.quit = tk.Button( self, text="QUIT", fg="red", command=root.destroy )
		self.quit.grid( row=self.row_quit, rowspan=self.span_quit,
				   column=self.col_button, columnspan=self.span_button,
				   sticky="nsew" )

		# Set defaults
		self.set_defaults()

	# Do serial setup
	def do_serial_setup( self ):
		
		# Set columns and rows
		for x in range(5):
			
			self.rowconfigure( x, weight=2, uniform=1 )

		for y in range(4):

			self.columnconfigure( y, weight=1, uniform=1 )
		
		
		# Port name menu
		self.portlabel = tk.Label( self, text="Port:" ).grid( row=self.row_port, column=self.col_label,
													    rowspan=self.span_port, columnspan=self.span_label,
													    sticky="w" )
		self.port_menu = tk.OptionMenu( self, self.portalias, *self.port_name )
		self.port_menu.grid( row=self.row_port, column=self.col_option,
							 rowspan=self.span_port, columnspan=self.span_option,
							 sticky="we" )
	
		# Baud rate menu
		self.baudlabel = tk.Label( self, text="Speed:" ).grid( row=self.row_baud, column=self.col_label,
														 rowspan=self.span_baud, columnspan=self.span_label,
														 sticky="w" )
		self.baud_menu = tk.OptionMenu( self, self.baudrate, *self.baud_opt )
		self.baud_menu.grid( row=self.row_baud, column=self.col_option,
							 rowspan=self.span_baud, columnspan=self.span_option,
							 sticky="w" )
		
		# Parity options
		self.paritylabel = tk.Label( self, text="Parity:").grid( row=self.row_parity, column=self.col_label,
														   rowspan=self.span_parity, columnspan=self.span_label,
														   sticky="w" )
		self.paritycheckE = tk.Checkbutton( self, text="Even", variable=self.parityeven,
										    command=self.seteven, onvalue = 1, offvalue = 0 )
		self.paritycheckO = tk.Checkbutton( self, text="Odd", variable=self.parityodd,
										    command=self.setodd, onvalue = 1, offvalue = 0 )
		self.paritycheckN = tk.Checkbutton( self, text="None", variable=self.paritynone,
										    command=self.setnone, onvalue = 1, offvalue = 0 )
		self.paritycheckE.grid( row=self.row_parity, column=self.col_option,
							    rowspan=self.span_parity, columnspan=1,
							    sticky="w" )
		self.paritycheckO.grid( row=self.row_parity, column=self.col_option+1,
								rowspan=self.span_parity, columnspan=1,
								sticky="w" )
		self.paritycheckN.grid( row=self.row_parity, column=self.col_option+2,
							    rowspan=self.span_parity, columnspan=1,
							    sticky="w" )
								


		# Bits menu
		self.bitslabel = tk.Label( self, text="Bits:" ).grid( row=self.row_bits, column=self.col_label,
														 rowspan=self.span_bits, columnspan=self.span_label,
														 sticky="w" )
		self.bits7 = tk.Checkbutton( self, text="7", variable=self.nbits,
											command=self.set7, onvalue = 7, offvalue = 8 )
		self.bits8 = tk.Checkbutton( self, text="8", variable=self.nbits,
											command=self.set8, onvalue = 8, offvalue = 7 )
		self.bits7.grid( row=self.row_bits, column=self.col_option,
						 rowspan=self.span_bits, columnspan=1,
						 sticky="w" )
		self.bits8.grid( row=self.row_bits, column=self.col_option+1,
						 rowspan=self.span_bits, columnspan=1,
						 sticky="w" )
							
		# Connect button
		self.connect = tk.Button( self, text="CONNECT", fg="green", command=self.connect_to_port )
		self.connect.grid( row=self.row_connect, rowspan=self.span_connect,
						   column=self.col_button, columnspan=self.span_button,
						   sticky="nsew" )
		
		# Disconnect button
		self.disconnect = tk.Button( self, text="DISCONNECT", fg="red", command=self.disconnect_port )
		self.disconnect.grid( row=self.row_disconnect, rowspan=self.span_disconnect,
							  column=self.col_button, columnspan=self.span_button,
							  sticky="nsew" )


	# Create buttons
	def create_target_buttons( self ):
		
		# Alpha source
		self.alpha = tk.Button( self, text="Alpha source", fg="purple", command=lambda:self.select_pos(0) )
		self.alpha.grid( row=self.row_target, column=0, sticky="nsew" )
		
		# Position 1
		self.pos1 = tk.Button( self, text="Position 1", fg="purple", command=lambda:self.select_pos(1) )
		self.pos1.grid( row=self.row_target, column=1, sticky="nsew" )
		
		# Position 1
		self.pos2 = tk.Button( self, text="Position 2", fg="purple", command=lambda:self.select_pos(2) )
		self.pos2.grid( row=self.row_target, column=2, sticky="nsew" )
	

	###########
	# Actions #
	###########
	
	# set the parity to even
	def seteven( self ):
		
		self.parity.set("PARITY_EVEN")
		self.parityodd.set(0)
		self.parityeven.set(1)
		self.paritynone.set(0)
	
	# set the parity to odd
	def setodd( self ):
		
		self.parity.set("PARITY_ODD")
		self.parityodd.set(1)
		self.parityeven.set(0)
		self.paritynone.set(0)
	
	# set the parity to none
	def setnone( self ):
		
		self.parity.set("PARITY_NONE")
		self.parityodd.set(0)
		self.parityeven.set(0)
		self.paritynone.set(1)
	
	# set the number of bits to 7
	def set7( self ):
		
		self.nbits.set("SEVENBITS")
	
	# set the number of bits to 8
	def set8( self ):
		
		self.nbits.set("EIGHTBITS")
	
	# Create serial port
	def connect_to_port( self ):
		
		self.serial_port.port = self.portalias.get()			# set name of port
		self.serial_port.baudrate = int( self.baudrate.get() )	# set baud rate
		self.serial_port.parity = int( self.parity.get() )		# set parity
		self.serial_port.bytesize = int( self.nbits.get() )		# set bytesize
		self.serial_port.open()									# open the port
	
	# Disconnect from serial port
	def disconnect_port( self ):
		
		self.serial_port.close()	# close the port

	# go to position 1
	def select_pos( self, pos ):
	
		print( "moving to position", pos )


	############
	# Defaults #
	############

	def set_defaults( self ):

		self.setodd()
		self.set7()
		self.baudrate.set( "9600" ) # initial value
		self.portalias.set( self.port_opt[0].device )	# initial value


##################
# Main programme #
##################

root = tk.Tk()
app = Application( master = root )
app.mainloop()
