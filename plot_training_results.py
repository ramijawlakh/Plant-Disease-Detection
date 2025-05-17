import pandas as pd
import matplotlib.pyplot as plt

# Load training results
df = pd.read_csv("/home/techoffice/Desktop/Rami/Senior2/runs/medium model/train/medium_plant_disease_exp/results.csv")

# Plot metrics (Modify based on available columns)
plt.plot(df["epoch"], df["metrics/mAP50-95(B)"], label="mAP@50-95")
plt.plot(df["epoch"], df["metrics/precision(B)"], label="Precision")
plt.plot(df["epoch"], df["metrics/recall(B)"], label="Recall")

plt.xlabel("Epoch")
plt.ylabel("Score")
plt.legend()
plt.title("Training Performance")

# Save results.png
plt.savefig("/home/techoffice/Desktop/Rami/Senior2/runs/medium model/train/medium_plant_disease_exp/results.png")
plt.show()
