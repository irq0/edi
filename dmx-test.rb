#!/usr/bin/env ruby
require "serialport"

def w(channel, r,g,b)
	@serial.write(sprintf("C%03dL%03d", channel-1, 0))
	@serial.write(sprintf("C%03dL%03d", channel+0, r))
	@serial.write(sprintf("C%03dL%03d", channel+1, g))
	@serial.write(sprintf("C%03dL%03d", channel+2, b))
	@serial.write(sprintf("C%03dL%03d", channel+3, 0))
end

channel = ARGV[0].to_i
puts channel
value = 
@serial = SerialPort.new("/dev/ttyUSB0", 38400)
@serial.write('B0')
while true do
	w(channel, 255, 255, 255)
	sleep(1)
	w(channel, 255, 0, 0)
	sleep(1)
	w(channel, 0, 255, 0)
	sleep(1)
	w(channel, 0, 0, 255)
	sleep(1)
	w(channel, 0, 0, 0)
	sleep(1)
end

