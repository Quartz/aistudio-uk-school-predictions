import boto
from boto.s3.key import Key
import csv

conn = boto.s3.connect_to_region('us-east-1')
bucket = conn.get_bucket('qz-aistudio-jbfm-scratch')

with open('open_schools.csv', 'w') as school_csv:
    writer = csv.writer(school_csv)
    header = ['label', 'school', 'filename', 'text']
    writer.writerow(header)

    root = bucket.list('schools/open/','/')
    for dir in root: # traverse through open and closed dirs
        row = []
        bucket = conn.get_bucket('qz-aistudio-jbfm-scratch')
        d = bucket.list(dir.name,'/')
        for subdir in d: # traverse through schools
            if subdir.name == "schools/":
                continue
            bucket = conn.get_bucket('qz-aistudio-jbfm-scratch')
            schools = bucket.list(subdir.name,'/')
            for school in schools:
                if school.name == "schools/closed/" or school.name == "schools/closed/.DS_Store":
                    continue
                if school.name == "schools/open/" or school.name == "schools/open/.DS_Store":
                    continue
                label = subdir.name.split('/')[1] # Get the label
                schoolname = school.name.split('/')[-2]
                files = bucket.list(school.name, '/')
                for f in files:
                    schoolname = schoolname.replace(',','')
                    filename = f.name.split('/')[-1]
                    filename = filename.replace('.txt','')
                    row = [label, schoolname, filename]
                    try:
                        k = Key(bucket) # Make a key to the S3 bucket
                        k.key = f.name
                        k.open()
                        content = k.read()
                        content = content.decode('utf-8')
                        content = content.replace('\n','') # Remove whitespace
                        content = content.replace(',','') # Remove commas for csv
                        row.append(content)
                        writer.writerow(row)
                        print ("Data for {} written to CSV file".format(schoolname))
                        print ("School label: {}".format(label))
                    except:
                        print ("error occurred. printing filename...")
                        print (f.name)
