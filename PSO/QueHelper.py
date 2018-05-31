#!/usr/bin/env python
import os, sys, subprocess, time

from common import *

class QueHelper:
  def __init__(self,RunSystem):
    self.RunSystem=RunSystem

    self.ExecLines = []

    self.ConfigLines = []

    self.RunLines = []

    # change if you want to use a different CMSSW Version
    self.CMSSW_BASE = os.environ['CMSSW_BASE']
    self.SCRAM_ARCH = os.environ['SCRAM_ARCH']
    print("\n----------------------------------------\n")
    print "using CMSSW_BASE="+self.CMSSW_BASE
    print "using SCRAM_ARCH="+self.SCRAM_ARCH
    print "might not be the right choice, depending on your linux, target linux and CMSSW Version"
    print "changeable in QueHelper.py"

    if RunSystem=="EKPSL5":
      thisPortal=os.environ["HOSTNAME"]
      if thisPortal=="ekpcms5":
        thisque=os.environ["SGE_CLUSTER_NAME"]
        if thisque!="p_ogs1111":
          print "you need to setup the sl5 que first"
          print "source /opt/sge62/ekpcluster/common/settings.sh"
          exit(1)
      elif thisPortal=="ekpcms6":
        print "using sl5 que on ekpcms6 might lead to problems"
        thisque=os.environ["SGE_CLUSTER_NAME"]
        if thisque!="p_ogs1111":
          print "you need to setup the sl5 que first"
          print "source /opt/sge62/ekpcluster/common/settings.sh"
          exit(1)
      else:
        print "dont know this portal"
        exit(1)
      self.ExecLines=[
          "export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n",
          "export SCRAM_ARCH="+self.SCRAM_ARCH+"\n",
          "source $VO_CMS_SW_DIR/cmsset_default.sh\n",
          "cd "+self.CMSSW_BASE+"/src\n",
          "eval `scram runtime -sh`\n"
          ]
      self.RunLines=[
          "qsub -cwd -S /bin/bash -o INSERTPATHHERE/logs/\$JOB_NAME.o\$JOB_ID -e INSERTPATHHERE/logs/\$JOB_NAME.e\$JOB_ID -q 'medium' INSERTEXECSCRIPTHERE\n"
          ] 
    elif RunSystem=="EKPSL6":
      thisPortal=os.environ["HOSTNAME"]
      #print thisPortal
      if thisPortal!="ekpcms6":
        print "WARNING"
        print "you try to start jobs on the ekp SL6 que from ekpcms5"
        print "do it from ekpcms or manually change QueHelper.py"
      thisque=os.environ["SGE_CLUSTER_NAME"]
      if thisque!="p_ogs1111_sl6":
          print "you need to setup the sl6 que first"
          print "source /opt/ogs_sl6/ekpclusterSL6/common/settings.sh"
          exit(1)
      self.ExecLines=[
          "export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n",
          "export SCRAM_ARCH="+self.SCRAM_ARCH+"\n",
          "source $VO_CMS_SW_DIR/cmsset_default.sh\n",
          "cd "+self.CMSSW_BASE+"/src\n",
          "eval `scram runtime -sh`\n"
          ]
      self.RunLines=[
          "qsub -cwd -S /bin/bash -o INSERTPATHHERE/logs/\$JOB_NAME.o\$JOB_ID -e INSERTPATHHERE/logs/\$JOB_NAME.e\$JOB_ID -q 'medium' INSERTEXECSCRIPTHERE\n"
          ]

    elif RunSystem == "NAFSL6":

      self.ExecLines = [

        "#!/bin/bash\n",
        "source /etc/profile.d/modules.sh\n",
        "module use -a /afs/desy.de/group/cms/modulefiles/\n",
        "module load cmssw/"+self.SCRAM_ARCH+"\n",
        "export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n",
        "export SCRAM_ARCH="+self.SCRAM_ARCH+"\n",
        "source $VO_CMS_SW_DIR/cmsset_default.sh\n",
        "cd "+self.CMSSW_BASE+"/src\n",
        "eval `scram runtime -sh`\n",
      ]

      # HTCondor getenv=True does not export LD_LIBRARY_PATH
      # --> added by hand in the script itself
      if 'LD_LIBRARY_PATH' in os.environ:
         self.ExecLines += ['export LD_LIBRARY_PATH='+os.environ['LD_LIBRARY_PATH']]

      self.ConfigLines = [

        'batch_name = INSERTNAMEHERE',

        'executable = INSERTEXECSCRIPTHERE',

        'output = INSERTPATHHERE/logs/INSERTNAMEHERE'+'.out.'+'$(Cluster).$(Process)',
        'error  = INSERTPATHHERE/logs/INSERTNAMEHERE'+'.err.'+'$(Cluster).$(Process)',
        'log    = INSERTPATHHERE/logs/INSERTNAMEHERE'+'.log.'+'$(Cluster).$(Process)',

        '#arguments = ',

        'transfer_executable = True',

        'universe = vanilla',

        'getenv = True',

        'should_transfer_files   = IF_NEEDED',
        'when_to_transfer_output = ON_EXIT',

        'requirements = (OpSysAndVer == "SL6")',
        '#requirements = (OpSysAndVer == "SL6" || OpSysAndVer == "CentOS7")',

        ' RequestMemory  = 2G',
        '+RequestRuntime = 10800',

        'queue',
      ]

    elif RunSystem=="NAFSL5":
      self.ExecLines=[
        "#!/bin/bash",
        ". /etc/profile.d/modules.sh\n",
        "module use -a /afs/desy.de/group/cms/modulefiles/\n",
        "module load cmssw/"+self.SCRAM_ARCH+"\n",
        "export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n",
        "export SCRAM_ARCH="+self.SCRAM_ARCH+"\n",
        "source $VO_CMS_SW_DIR/cmsset_default.sh\n",
        "cd "+self.CMSSW_BASE+"/src\n",
        "eval `scram runtime -sh`\n"
      ]

      qsub_opts = [
        '-S /bin/bash',
        '-V',
#        '-pe local 4-8',
        '-l h_vmem=4G',
        '-l h_fsize=1G',
        '-l h_rt=96:00:00',
      ]

      self.RunLines = [
        'qsub '+' '.join(qsub_opts)+' -l os=sld5 -o INSERTPATHHERE/logs/\$JOB_NAME.o\$JOB_ID -e INSERTPATHHERE/logs/\$JOB_NAME.e\$JOB_ID INSERTEXECSCRIPTHERE\n'
      ] 

    else:
      print "could not set up the batch system ", self.RunSystem
      print "check QueHelper.py"
      exit(1)

    print "set up QueHelper\n"

  def GetExecLines(self):
    return self.ExecLines

  def GetRunLines(self):
    return self.RunLines

  def GetConfigLines(self):
    return self.ConfigLines

  def StartJob(self, runScript):

    res = ''

    try:
      res=subprocess.check_output([runScript], shell=True)

    except (subprocess.CalledProcessError, OSError):
      print "could not submit the job"
      exit(1)

    res=res.split()

    jid=0

    for r in res:
      if r.isdigit():
        jid=int(r)
        break

    return jid

  def GetIsJobRunning(self, jobID, fpath):

    if which('qstat', permissive=True, warn=False) != None:

       try:
         bufferfile = open(fpath, 'w')

         res = subprocess.check_output(["qstat", "-j", str(jobID)], stderr=bufferfile)

         bufferfile.close()

         return bool(res != '')

       except (subprocess.CalledProcessError):
         return False

       except:
         print "ERROR during qstat"
         print sys.exc_info()[0]
         exit(1)

    else:

       htc_jobIDs = HTCondor_jobIDs(os.environ['USER'], permissive=True)

       while htc_jobIDs == None:

          WARNING('QueHelper.py -- call to "condor_q" failed, will wait 60sec and try again')

          time.sleep(60)

          htc_jobIDs = HTCondor_jobIDs(os.environ['USER'], permissive=True)

       if str(jobID) in htc_jobIDs: return True

    return False
