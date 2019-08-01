import os
import re
import pandas as pd

closed_root = '/picstorage/schools/closed/'
open_root = '/picstorage/schools/open/'
last = []
rest = []
last_files = []
rest_files = []
last_names = []
rest_names = []
roots = [closed_root, open_root]

for root in roots:
    for path, subdirs, files in os.walk(root):
        for s in subdirs:
            f = os.path.join(path, s)
            for p2, s2, f2 in os.walk(f):
                m = [int(f.replace(".txt","")) for f in f2 if f != ' ']
                if not m:
                    continue
                most_recent = max(m)
                for file in f2:
                    if file == '':
                        continue
                    content = open(os.path.join(p2,file),'r').read()
                    if re.search("childminder",content,re.IGNORECASE):
                        continue
                    if re.search("converter",content,re.IGNORECASE):
                        continue
                    if content == '':
                        continue
                    content = content.replace('\n','')
                    if file == str(most_recent)+".txt":
                        last_files.append(most_recent)
                        last.append(content)
                        last_names.append(s)
                    else:
                        rest_files.append(int(file.replace(".txt","")))
                        rest.append(content)
                        rest_names.append(s)

last_labels = ["last" for i in range(len(last))]
df_last = pd.DataFrame()
df_last["school"] = last_names
df_last["text"] = last
df_last["file"] = last_files
df_last["label"] = last_labels

rest_labels = ["not_last" for i in range(len(rest))]
df_rest = pd.DataFrame()
df_rest["school"] = rest_names
df_rest["text"] = rest
df_rest["file"] = rest_files
df_rest["label"] = rest_labels

df = df_last.append(df_rest, ignore_index=True)
df.to_csv('last_reports.csv')
