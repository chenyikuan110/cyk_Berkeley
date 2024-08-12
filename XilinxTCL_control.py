# Original Author @Paebbels in Dec 2015
import subprocess

class XilinxTCLShellProcess(object):
  # executable = "sortnet_BitonicSort_tb.exe"
  executable = r"C:\Xilinx\14.7\ISE_DS\ISE\bin\nt64\xtclsh.exe"
  boundarString = "POC_BOUNDARY"
  boundarCommand = bytearray("puts {0}\n".format(boundarString), "ascii")

  def create(self, arguments):
    sysargs = [self.executable]

    self.proc = subprocess.Popen(sysargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    self.sendBoundardCommand()

    while(True):
      stdoutLine = self.proc.stdout.readline().decode()
      if self.boundarString in stdoutLine:
        break
    print("found boundary string")

  def terminate(self):
    self.proc.terminate()

  def sendBoundardCommand(self):
    self.proc.stdin.write(self.boundarCommand)
    self.proc.stdin.flush()

  def sendCommand(self, line):
    command = bytearray("{0}\n".format(line), "ascii")
    self.proc.stdin.write(command)
    self.sendBoundardCommand()

  def sendLine(self, line):
    self.sendCommand(line)

    while(True):
      stdoutLine = self.proc.stdout.readline().decode()
      print("stdoutLine='{0}'".format(stdoutLine))
      if stdoutLine == "":
        print("reached EOF in stdout")
        break
      elif "vhdl" in stdoutLine:
        print("found a file name")
      elif (self.boundarString in stdoutLine):
        print("output consumed until boundary string")
        break

def main():
  print("creating 'XilinxTCLShellProcess' instance")
  xtcl = XilinxTCLShellProcess()

  print("launching process")
  arguments = []
  xtcl.create(arguments)

  i = 1
  while True:
    print("press ENTER for the next step")
    from msvcrt import getch
    from time import sleep
    sleep(0.1)  # 0.1 seconds

    key = ord(getch())
    if key == 27:    # ESC
      print("aborting")
      print("sending 'exit'")
      xtcl.sendLine("exit")
      break
    elif key == 13: # ENTER
      if (i == 1):
        #print("sending 'project new test.xise'")
        #xtcl.sendLine("project new test.xise")
        print("sending 'project open PoCTest.xise'")
        xtcl.sendLine("project open PoCTest.xise")
        i += 1
      elif (i == 2):
        print("sending 'lib_vhdl get PoC files'")
        xtcl.sendLine("lib_vhdl get PoC files")
        i += 1
      elif (i == 3):
        print("sending 'search *.vhdl -type file'")
        xtcl.sendLine("search *.vhdl -type file")
        i += 1
      elif (i == 4):
        print("sending 'xfile add ../../src/common/strings.vhdl -lib_vhdl PoC -view ALL'")
        xtcl.sendLine("xfile add ../../src/common/strings.vhdl -lib_vhdl PoC -view ALL")
        i += 16
      elif (i == 20):
        print("sending 'project close'")
        xtcl.sendLine("project close")
        i += 1
      elif (i == 21):
        print("sending 'exit'")
        xtcl.sendCommand("exit")
        break

  print("exit main()")
  xtcl.terminate()

  print("the end!")

# entry point
if __name__ == "__main__":
  main()