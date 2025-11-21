import csv
import matplotlib.pyplot as plt

modes = {"no_dnssec": [], "dnssec": []}

with open("measurements.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        mode = row["mode"]
        if row["poisoned"] == "1" and row["time_to_poison_ms"]:
            modes[mode].append(float(row["time_to_poison_ms"]))

labels = []
values = []

for mode, times in modes.items():
    labels.append(mode)
    values.append(len(times))

plt.bar(labels, values)
plt.ylabel("Number of successful poisonings")
plt.title("Poisoning success: no DNSSEC vs DNSSEC")
plt.savefig("poison_success.png")
print("[+] Saved poison_success.png")

