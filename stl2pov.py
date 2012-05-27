#! /usr/bin/env python
# -*- python coding: utf-8 -*-
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

'''Program for converting an STL file into a POV-ray mesh or mesh2.'''

import sys
import os
import time
import stl

ver = ('stl2pov [ver. ' + '$Revision$'[11:-2] + 
       '] ('+'$Date$'[7:-2]+')')

def usage():
    print ver
    print "Usage: stl2pov infile [outfile]"

def mesh1(s):
    '''Returns a string containing the Surface s as a POV-ray mesh object.'''
    ms = "# declare m_{} = mesh {{\n".format(s.name)
    sot = "  triangle {{ // #{}\n"
    fc = "    <{1}, {0}, {2}>,\n"
    fct = "    <{1}, {0}, {2}>\n"
    for n, f in enumerate(s.facets):
        ms += sot.format(n+1)
        ms += fc.format(f.v[0].x, f.v[0].y, f.v[0].z)
        ms += fc.format(f.v[1].x, f.v[1].y, f.v[1].z)
        ms += fct.format(f.v[2].x, f.v[2].y, f.v[2].z)
        ms += "  }\n"
    ms += "}\n"
    return ms

def mesh2(s):
    '''Returns a string containing the Surface s as a POV-ray mesh2 object.'''
    ms = "# declare m_{} = mesh2 {{\n".format(s.name)
    numkeys = [(i, k) for (i, k) in enumerate(s.vertices.keys())]
    ms += '  vertex_vectors {\n'
    ms += '    {},\n'.format(len(numkeys))
    for (i, k) in numkeys:
        ms += '    <{1}, {0}, {2}>,'.format(s.vertices[k].x, s.vertices[k].y, 
                                          s.vertices[k].z)
        ms += ' // vertex #{}\n'.format(i)
    i = ms.rindex(', //')
    ms = ms[:i]
    ms += '  // vertex #{}\n'.format(len(numkeys)-1)
    ms += '  }\n'
    keydict = { k : i for (i, k) in numkeys}
    flist = [(keydict[fc.v[0].key()], keydict[fc.v[1].key()], 
              keydict[fc.v[2].key()]) for fc in s.facets]
    ms += '  face_indices {\n'
    ms += '    {},\n'.format(len(flist))
    for (a, b, c) in flist:
        ms += '    <{}, {}, {}>,\n'.format(a, b, c)
    ms = ms[:-2]
    ms += '\n  }\n}\n'
    return ms

# Process the command line arguments
if len(sys.argv) == 1:
    usage()
    sys.exit(0)
oldmesh = True
if sys.argv[1] == '-2':
    oldmesh = False
    del sys.argv[1]
# Read the STL file
try:
    stlobj = stl.Surface(sys.argv[1])
except:
    print "The file '{}' cannot be read or parsed. Exiting.".format(sys.argv[1])
    sys.exit(1)
# Process the file
for result in stlobj.processfacets:
    print result
# Remove spaces from name
stlobj.name = stlobj.name.replace(' \t', '_')
# Generate output
outs = "// Generated by {} on {}.\n".format(ver, time.asctime())
outs += stlobj.stats('// ')+'\n'
outs += "// The abovementioned coordinates are in the STL file's right-handed\n"
outs += "// coordinate system, while POV-ray uses a left-handed system.\n"
outs += "// You should swap the x and y above to get POV-ray coordinates.\n"
if oldmesh:
    outs += mesh1(stlobj)
else:
    outs += mesh2(stlobj)
# Write output to file.
if len(sys.argv) < 3:
    # Derive output name
    outbase = os.path.basename(sys.argv[1])
    if outbase.endswith((".stl", ".STL")):
        outbase = outbase[:-4]
    outfile = outbase+".inc"
# Or to a named output file.
else:
    outfile = sys.argv[2]
try:
    outf = open(outfile, "w+")
    outf.write(outs)
    outf.close()
except:
    print "Cannot write output file '{}'".format(sys.argv[2])
    sys.exit(2)
