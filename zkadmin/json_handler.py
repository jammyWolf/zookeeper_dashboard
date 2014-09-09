#encoding: utf-8

import json
  
def decode(sdata, path='?'):
    '''
    Code from zc.zk, authored by @Jim Fulton. 
    '''

    s = sdata.strip()
    if not s:
        data = {}
    elif s.startswith('{') and s.endswith('}'):
        try:
            data = json.loads(s)
        except:
            data = dict(string_value = sdata)
    else:
        data = dict(string_value = sdata)
    return data

def main():
    print load_cluster("interface.json")

if __name__ == "__main__":
    main()


  
  
 
  
  
  
  
  
  
  
  
  
  
  
 

