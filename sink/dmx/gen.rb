#!/usr/bin/env ruby
# -*- coding: utf-8 -*-

File.open('programs/alarm', 'w') { |f| 
  (0..255).step(10) do |n|
    f.write(format("#%02x0000\n", n))
  end
  f.write(format("#%02x0000\n", 255))
  255.step(0, -10) do |n|
    f.write(format("#%02x0000\n", n))
  end
}

#das schreibt das background-Programm für einen Tag raus.
#Sollte reichen...
File.open('programs/background', 'w') { |f|
  got = {}
  bgsteps = [0.1, 0.2, -0.3]
  bgvals = [100, 100, 100]
  i=0
  (0..86400).each do |d|
    i += 1
    puts i if (i % 100000) == 0
    (0..2).each { |i|
      bgvals[i] += bgsteps[i]
      if bgvals[i] >= 255
        bgvals[i] = 255
        bgsteps[i] *= -1
      end
      if bgvals[i] <= 0
        bgvals[i] = 0
        bgsteps[i] *= -1
      end
    }
    f.write(format("#%02x%02x%02x\n", *bgvals))
  end
}

#bgsteps = [0.1, 0.2, -0.3]
#bgvals = [100, 100, 100]
#def background(device):
#    global bgvals
#    global bgsteps
#            
#    for i in range(0,3):
#        bgvals[i] = bgvals[i] + bgsteps[i]
#        if bgvals[i] >= 255:
#            bgvals[i] = 255
#            bgsteps[i] *= -1
#        if bgvals[i] <= 0:
#            bgvals[i] = 0
#            bgsteps[i] *= -1
#    rgb(int(bgvals[0]), int(bgvals[1]), int(bgvals[2]))
#    time.sleep(0.1)

