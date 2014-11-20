#!/usr/bin/env ruby
# -*- coding: utf-8 -*-

File.open('programs/alarm', 'w') { |f| 
  (0..255).each do |n|
    f.write(format("#%02x0000\n", n))
  end
  f.write(format("#%02x0000\n", 255))
  255.step(0, -1) do |n|
    f.write(format("#%02x0000\n", n))
  end
}
