import os


SRC_DIR='../doc-src'
DST_DIR='../doc'

for root, dirs, files in os.walk(SRC_DIR):
    for filename in files:
        print("Process", filename)
        in_file_path = os.path.join(SRC_DIR, filename)
        out_file_path = os.path.join(DST_DIR, filename)
        with open(in_file_path, 'r') as infile:
            with open(out_file_path, 'w') as outfile:
                for line in infile:
                    if line.find('%include') >= 0:
                        include_path = line.strip().split(" ")[1].strip()
                        include_file_path = os.path.join(SRC_DIR, include_path)
                        with open(include_file_path, 'r') as include_file:
                            content = include_file.read()
                        outfile.write(content)
                    else:
                        outfile.write(line)
