import time

from aminer import AMinerConfig
from aminer.util import PersistencyUtil

class NewMatchPathDetector:
  """This class creates events when new data path was found in
  a parsed atom."""

  def __init__(self, aminerConfig, anomalyEventHandlers, peristenceId='Default', autoIncludeFlag=False):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location."""
    self.anomalyEventHandlers=anomalyEventHandlers
    self.autoIncludeFlag=autoIncludeFlag
    self.nextPersistTime=None

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(aminerConfig, 'NewMatchPathDetector', peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.knownPathSet=set()
    else:
      self.knownPathSet=set(persistenceData)


  def receiveParsedAtom(self, atomData, match):
    unknownPathList=[]
    for path in match.getMatchDictionary().keys():
      if not(path in self.knownPathSet):
        unknownPathList.append(path)
        if self.autoIncludeFlag:
          self.knownPathSet.add(path)
    if len(unknownPathList)>0:
      if self.nextPersistTime==None:
        self.nextPersistTime=time.time()+600
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.NewMatchPathDetector', 'New path(es) %s ' % (', '.join(unknownPathList)), [atomData], match)


  def checkTriggers(self):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime==None: return(600)

    delta=self.nextPersistTime-time.time()
    if(delta<0):
      PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime=None