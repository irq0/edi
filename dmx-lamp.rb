#!/usr/bin/env ruby 
# encoding: UTF-8

#Programme: 0 = background, 1 = testprogram, 42 = alarm

#        self.alarmval += self.alarmstep
#        if self.alarmval >= 300:
#            self.alarmstep *= -1
#        elif self.alarmval <= 0:
#            self.alarmstep *= -1
#        rgb(self.alarmval, 0, 0)
#        time.sleep(0.01)


#TODO Farbprogramme
#TODO testen, ob enabled/disabled state auch regelmäßig aufs dmx geschrieben werden muss

#key dmx.lamp.subraum.control, body ~= (on|off)
#key dmx.lamp.subraum.0, body ~= \d,\d,\d

#config
$subsystem = "subraum"
$program_path = './programs/'
$channel_write_interval = 0.1
$program_step_ratio = 10
#/config

require "bunny"
require "serialport"
require "thread"
require "json"

class SerialDummy
  def initialize(dev, bauds)
    puts "Opened #{dev}@#{bauds}"
  end
  def write(s)
    puts "Serial write: #{s}"
  end
end

class DmxControl
  def initialize
#    @serial = SerialPort.new("/dev/dmx", 38400)
    @serial = SerialDummy.new("/dev/dmx", 38400)
    @sema = Mutex.new #semaphore die @serial schützt
    @channels = {}
    @programs = {}
    @enabled = true
  end

  def on
    @sema.synchronize {
      @enabled = true
      @serial.write('B0')
    }
  end

  def off
    @sema.synchronize {
      @enabled = false
      @serial.write('B1')
    }
  end

  def setchannel(channel, value)
    @channels[channel] = value
  end

  def setprogram(channel, color)
    @programs[channel] = color
    setchannels
  end

  def loop
    i=0
    while true
      sleep($channel_write_interval)
      next unless @enabled
      i = (i + 1) % $program_step_ratio
      advanceprograms if i == 0 
      @sema.synchronize {
        @channels.each_pair do |channel, value|
          @serial.write(sprintf("C%03dL%03d", channel, value))
        end
      }
    end
  end

  private
  
  def advanceprograms
    @programs.each_pair do |channel, color|
      channel.next
    end
    setchannels
  end

  def setchannels
    @programs.each_pair do |channel, color|
      setrgb(channel, *color.current)
    end
  end

  def setrgb(channel, r, g, b)
    r = 255 if r > 255
    r = 0 if r < 0
    g = 255 if g > 255
    g = 0 if g < 0
    b = 255 if b > 255
    b = 0 if b < 0
    puts "setrgb, #{channel}, #{r}, #{g}, #{b}"
    setchannel(channel-1, 0)
    setchannel(channel+0, r)
    setchannel(channel+1, g)
    setchannel(channel+2, b)
    setchannel(channel+3, 0)
  end

end

class Color
  @@colors = {}

  def self.resolve(color)
    col = simple_resolve(color)
    puts col
    return Color.new([col]) if col
    program = File.join($program_path,color)
    return Color.new(program) if File.exist?(program)
    fail "Unbekannte Farbe: #{color}"
  end
  def self.simple_resolve(color)
    color.downcase!
    return @@colors[color] if @@colors.include?(color)
    m = /(\d+),(\d+),(\d+)/.match(color)
    return m[1..3].map{|e| e.to_i} if m
    m = /#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.match(color)
    return m[1..3].map{|e| e.to_i(16)} if m
    JSON.load(color)[0..2].map{ |e| e.to_i } rescue nil
  end
  def self.load_colors
    @@colors = Hash[File.open('colors.txt').each_line.map do |line|
      m = /([^ ]+)\s+(#[a-fA-F0-9]{6})/.match(line)
      [m[1], simple_resolve(m[2])] if m
    end.compact]
  end

  def initialize(colors)
    if colors.is_a? String
      @colors = []
      @index = 0
      File.open(colors).each do |line|
        c = Color.simple_resolve(line.strip)
        @colors << c if c
      end
    else
      @colors = colors.map { |l| l.map { |e| e.to_i } }
      @index = 0
    end
    fail "Hab keine Farben!" if @colors.length == 0
  end
  def current
    return @colors[@index]
  end
  def next
    @index = (@index + 1) % @colors.length
  end
end

Color.load_colors

if __FILE__ == $0
  rkprefix = "dmx.lamp."+$subsystem+"."
  control = DmxControl.new

  conn = Bunny.new(:host => "mopp")
  conn.start
  ch = conn.create_channel
  xchg = ch.topic("act_dmx", :auto_delete => true)
  q = ch.queue("act_dmx_subraum", :auto_delete => true)
  q.bind(xchg, :routing_key => rkprefix+"*").subscribe do |info, meta, data|
    rk = info.routing_key
    if rk == rkprefix+"control"
      case data
      when "on" then
        control.on
      when "off" then
        control.off
      end
      next
    end
    lamp = rk[rkprefix.length..-1]
    next unless lamp
    begin
      program = Color.resolve(data)
      puts "Setting #{lamp} to #{program}"
      control.setprogram(lamp.to_i, program)
    rescue => err
      puts err
    end
  end
  
  control.loop
  conn.close
end
