count = 0
with open('all_results.csv', 'r') as f:
    with open('all_results_with_source.csv', 'w+') as w:
        for line in f:
            if 0 <= count <= 138:
                w.write(line.strip() + ",Reuters\n")
            elif 139 <= count <= 253:
                w.write(line.strip() + ",Economist\n")
            elif 254 <= count <= 420:
                w.write(line.strip() + ',CNN\n')
            else:
                w.write(line.strip() + ',FOX\n')
            count += 1
