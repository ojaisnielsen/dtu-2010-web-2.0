'''
Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 


lingpipe.py provides a wrapper class for LingPipe (otherwise, a java application) in Python
'''

import os
import subprocess
import re

class LingPipeWarper:

    def __init__(self, lingPipePath):
        self._lingPipePath = os.path.abspath(lingPipePath)

    def parseNamedEntities(self, input, type):
        shellExt = {"nt": "bat", "posix": "sh"}        
        workingDir = os.path.join(self._lingPipePath, "demos/generic/bin")
        program = "cmd_ne_en_news_muc6.%s \"-contentType=%s\" \"-outCharset=utf-8\" \"-inCharset=utf-8\"" % (shellExt[os.name], type)
        lingpipe = subprocess.Popen(program, cwd = workingDir, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
        lingpipe.stdin.write(input.encode("UTF-8"))
        lingpipe.stdin.close()
        output = re.split("<\?xml.*?\?>", lingpipe.stdout.read(), 1)[1]
        lingpipe.stdout.close()
        return output;
    
if __name__ == "__main__":
    lingPipe = LingPipeWarper("lingpipe-3.8.2")
    print lingPipe.parseNamedEntities("John Smith lives in <b>Washington</b>. He works for Microsoft.", "text/html")

