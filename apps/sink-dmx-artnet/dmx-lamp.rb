#!/usr/bin/env ruby
# encoding: UTF-8

#TODO Farbprogramme
#TODO testen, ob enabled/disabled state auch regelmäßig aufs dmx geschrieben werden muss

#key dmx.lamp.subraum.control, body ~= (on|off)    # not supported
#key dmx.lamp.subraum.0, body ~= (\d,\d,\d|html-farbe|programmname)

# ArtNet
# see http://www.artisticlicence.com/WebSiteMaster/User%20Guides/art-net.pdf
# Art-Net™ Designed by and Copyright Artistic Licence Holdings Ltd

#config
def config
	$subsystem = "subraum"
	$program_path = './programs/'
	$channel_write_interval = 0.01
	$debug = false
	$lamps = [2, 6, 10, 14, 20]
	$default_colors = ["backgroundA","backgroundB","backgroundB","backgroundB","backgroundB"]
	$server = "172.31.65.70"
end  #/config

require "bunny"
require "socket"
require "thread"
require "json"

class DmxControl
  def initialize
    @socket = UDPSocket.new
    @sema = Mutex.new #semaphore die @serial schützt
    @channels = {}
    @programs = {}
    @enabled = true
    @maxchannel = 0
  end

  def on
    @sema.synchronize {
      $lamps.each_pair { |lampid, default|
        setprogram(lampid, default)
      }
      @enabled = true
    }
  end

  def off
    @sema.synchronize {
      @enabled = false
    }
  end

  def setchannel(channel, value)
    @channels[channel] = value
    if channel > @maxchannel then
      @maxchannel = channel
    end
  end

  def setprogram(channel, color)
    return unless $lamps.include? channel
    @programs[channel] = color
    setchannels
  end

  def loop
    while true
      sleep($channel_write_interval)
      next unless @enabled
      advanceprograms
      @sema.synchronize {
        #TODO make sure the string is not unicode
        msg = "Art-Net\0\0\x50\0\0\0\0\0\0\0\x00" + "\0"*@maxchannel
        msg[17] = (@maxchannel&0xff).chr
        msg[16] = ((@maxchannel>>8)&0xff).chr
        @channels.each_pair do |channel, value|
          msg[18+channel] = (value.to_i&0xff).chr
        end
        @socket.send(msg, 0, $server, 6454)
      }
    end
  end

  private

  def advanceprograms
    @programs.each_pair do |channel, color|
      color.next
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
    return Color.new([col]) if col
    p = File.join($program_path,color+".rb")
    if File.exist?(p) && File.realpath(p).start_with?($program_path) then
      c = load_color_subclass(p)
      return c if c
    end
    p = File.join($program_path,color)
    return Color.new(p) if File.exist?(p) && File.realpath(p).start_with?($program_path)
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
  def self.load_color_subclass(path)
    begin
      c = eval(IO.read(path)).new
      puts "loaded Class #{c.class.name} from #{path}"
      return c
    rescue
      puts $!
      puts $@
    end
  end
  def self.load_colors
    @@colors = Hash[File.open('colors.txt').each_line.map do |line|
      m = /([^ ]+)\s+(#[a-fA-F0-9]{6})/.match(line)
      [m[1].downcase, simple_resolve(m[2])] if m
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
      puts "loaded Program #{colors} with #{@colors.length} lines"
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

config
$program_path = File.realpath($program_path)
Color.load_colors
lamps = $lamps
$lamps = {}
lamps.each_index { |i| $lamps[lamps[i]] = Color.resolve($default_colors[i])}

if __FILE__ == $0
  rkprefix = "dmx.lamp."+$subsystem+"."
  control = DmxControl.new
  control.on

  conn = Bunny.new(:host => ENV.fetch("AMQP_SERVER", "mopp"))
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
