
#region Helper Classes
class ColourDict(dict):
    """
    This class is used to store the special colours. \n
    It is used to ensure that a missing colour does not cause a crash by returning the "Blue" colour. \n
    Only `__getitem__` is overwritten thus `.get` can still be used to detect missing colours and provide replacements.
    """
    def __getitem__(self, key):
        try:
            Colour = dict.__getitem__(self, key)
        except:
            for v in self.values():
                Colour = v
                break
        return Colour
    
    def copyFromDict(self, dict):
        for i,v in dict.items():
            self[i] = v

#endregion
